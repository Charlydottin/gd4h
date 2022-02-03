#!/usr/bin/.venv/python3.8

import os
from pymongo import MongoClient
from csv import DictReader, DictWriter
import json
from argostranslate import package, translate
import datetime
import bleach

DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]

AVAILABLE_LANG = ["fr","en"]
SWITCH_LANGS = dict(zip(AVAILABLE_LANG,AVAILABLE_LANG[::-1]))

installed_languages = translate.get_installed_languages()
fr_en = installed_languages[1].get_translation(installed_languages[0])
en_fr = installed_languages[0].get_translation(installed_languages[1])



curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
meta_dir = os.path.join(data_dir, "meta")
schema_dir = os.path.join(data_dir, "schemas")
dataset_dir = os.path.join(data_dir, "dataset")
organization_dir = os.path.join(data_dir, "organization")
model_dir = os.path.join(os.path.dirname(parent_dir), "back", "models")

def translate(text, _from="fr"):
    if _from == "fr":
        return fr_en.translate(text)
    else:
        return en_fr.translate(text)


def get_not_translated_fields(model="organization"):
    '''get all fields for given model that are not multilingual'''
    fields = DB.rules.find({"model": model, "translation": False}, {"slug":1})
    return [f["slug"] for f in fields]

def get_translated_fields(model="organization"):
    '''get all fields for given model that are multilingual'''
    fields = DB.rules.find({"model": model, "translation": True}, {"slug":1})
    return [f["slug"] for f in fields]

def get_mandatory_fields(model="organization"):
    fields = DB.rules.find({"model": model, "mandatory": True}, {"slug":1})
    return [f["slug"] for f in fields]

def get_rule(model, field_slug):
    '''get rule for given model and given field'''
    rule = DB.rules.find_one({"model": model, "slug": field_slug})
    return rule

def get_rules(model):
    '''get rule for given model and given field'''
    return list(DB.rules.find({"model": model},{"_id":0}))



def import_organizations():
    '''import_organizations
    insert organization defined by rules into DB.organizations from data/organizations/organizations_fr.csv
    '''
    DB.organizations.drop()
    org_doc = os.path.abspath(os.path.join(data_dir, "organizations", "organizations_fr.csv"))
    print(f"Create Organizations by inserting {org_doc}")
    with open(org_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            org = {"fr": {},"en": {}}
            org["fr"] = row
            org["en"] = {k: v for k,v in row.items() if get_not_translated_fields("organization")} 
            for translated_field in  get_translated_fields("organization"):
                rule = get_rule("organization", translated_field)
                try:
                    value = row[translated_field] 
                    if rule["is_controled"]:
                        accepted_ref = DB[rule["reference_table"]].find_one({"label_fr": value}, {"label_en":1})
                        try:
                            value = accepted_ref["label_en"]
                        except: 
                            value = accepted_ref
                except KeyError:
                    value = None
                org["en"][translated_field] = value
            db_org = DB.organizations.insert_one(org)
            # create_logs("admin","create", "organization", True, "OK", scope=None, ref_id=db_org.inserted_id)
    print(DB.organizations.count_documents({}), "organization inserted")


def cast_value(datatype, value):
    '''transform rules datatype into pydantic datatype'''
    if datatype == "string":
        return str(value)
    if datatype == "id":
        return str(value)
    if datatype =="boolean":
        if value is None:
            return None
        return bool(value)
    if datatype == 'date':
        if value is None:
            return ""
        return str(value)
    if datatype == "url":
        return str(value)
    if datatype == "email":
        return str(value)
    if datatype == 'object':
        return create_comment("admin", value)
        # return {"text":str(value), "user":{}}

def cast_type_given_rule(model, field, value):
    if field == "organizations":
        orgs = []
        for org in value.split("|"):
            o = DB.organizations.find_one({"fr.name": org})
            orgs.append(o)
        return orgs
    if "comments" in field:
        return [create_comment("admin", value)]
    rule = get_rule(model, field)
    if rule is None:
        if value in ["true", "false"]:
            return bool(value)
        return value
    if rule["multiple"]:
        return [cast_value(rule["datatype"], v) for v in value.split("|")]
    else:
        return cast_value(rule["datatype"], value)


def import_datasets():
    print("Create Datasets")
    created_datasets = []
    datasets_doc = os.path.abspath(os.path.join(data_dir, "datasets", "datasets_fr.csv"))
    with open(datasets_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            dataset = {"fr": {},"en": {}}
            dataset["fr"] = {k:cast_type_given_rule("dataset",k,v) for k,v in row.items()}
            dataset["en"] = {k:cast_type_given_rule("dataset",k,v) for k,v in row.items() if get_not_translated_fields("dataset")} 
            for translated_field in  get_translated_fields("dataset"):
                rule = get_rule("dataset", translated_field)
                try:
                    value = row[translated_field] 
                    if rule["is_controled"]:
                        accepted_ref = DB[rule["reference_table"]].find_one({"label_fr": value}, {"label_en":1})
                        try:
                            value = accepted_ref["label_en"]
                        except: 
                            value = accepted_ref
                except KeyError:
                    value = None
                dataset["en"][translated_field] = value
            DB.datasets.insert_one(dataset)
        print(DB.datasets.count_documents(), "datasets")

def link_organizations_to_datasets():
    not_found_orgs = []
    for dataset in DB.datasets.find({}, {"_id": 1, "organizations":1}):
        orgs = []
        for org in dataset["organizations"]:
            existing_org = DB.organizations.find_one({"name": org["name"]})
            
            if existing_org is None:
                not_found_orgs.append(org["name"])
                DB.logs.insert_one(create_logs("admin", "edit", "dataset", False, "Organization '{}' not found".format(org["name"]), scope="organizations", ref_id=dataset["_id"]))
            else:
                orgs.append(existing_org)
        log = create_logs("admin", "edit", "dataset", True, "OK", scope="organizations", ref_id=dataset["_id"])
        DB.datasets.update_one({"_id": dataset["_id"]},{"$set": {"organizations":orgs}})
        DB.logs.insert_one(log)
    print("Missing orgs ", set(not_found_orgs))
    
def register_dataset_comments():
    dataset = DB.datasets.find_one()
    comments_fields =  {key:1 for key in dataset if "comment" in key}
    comments_fields["_id"] = 1
    for dataset in DB.datasets.find({}, comments_fields):
        dataset_id = dataset["_id"]
        del dataset["_id"]
        for k,v in dataset.items():
            for c in v:
                register_comment(c, "dataset", k, dataset_id)

def translate_datasets():
    for dataset in DB.datasets.find({}):
        for k,v in dataset.items():
            if isinstance(v, dict):
                if v["label_en"] is None and v["label_fr"] is not None:
                    status, ref = find_reference_by_label_fr("ref_"+k, v["label_fr"])
                    if status:
                        v["label_en"] = ref["label_en"]
                    else:
                        v["label_en"] = translate(v["label_fr"])
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})
                    
                    continue
                elif v["label_fr"] is None and v["label_en"] is not None:
                    status, ref = find_reference_by_label_fr("ref_"+k, v["label_en"])
                    if status:
                        v["label_fr"] = ref["label_fr"]
                    else:
                        v["label_fr"] = translate(l["label_en"])
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})            
                    continue
                
            if isinstance(v, list):
                update = False
                if k not in ["organizations"]:
                    for l in v:    
                        if isinstance(l, dict):    
                            if l["label_en"] is None and l["label_fr"] is not None:
                                status, ref = find_reference_by_label_fr("ref_"+k, l["label_fr"])
                                if status:
                                    l["label_en"] = ref["label_en"]
                                else:
                                    l["label_en"] = translate(l["label_fr"])
                                update = True
                            elif l["label_fr"] is None and l["label_en"] is not None:
                                status, ref = find_reference_by_label_fr("ref_"+k, v["label_en"])
                                if status:
                                    l["label_fr"] = ref["label_fr"]
                                else:
                                    l["label_fr"] = translate(l["label_en"])
                                update = True
                if update:
                    DB.datasets.update_one({"_id": dataset["_id"]}, {"$set": {k:v}})            
                    continue
def translate_fr_references():
    print("Translate references from FR > EN")
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_en": ""},{"label_en": None}], "label_fr":{"$nin": ["", None]}}, {"_id":1, "label_fr":1}):
            try: 
                value_en = translate(ref_value["label_fr"], _from="fr")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_en": value_en} })
            except KeyError:
                pass
def translate_en_references():
    print("Translate references from EN > FR")
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_fr": ""},{"label_fr": None}], "label_en":{"$nin": ["", None]}}, {"_id":1, "label_en":1}):
            try: 
                
                value_fr = translate(ref_value["label_en"], _from="en")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_fr": value_fr} })
            except KeyError:
                pass

def translate_missing_references():
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_en": ""},{"label_en": None}], "label_fr":{"$nin": ["", None]}}, {"_id":1, "label_fr":1}):
            try: 
                value_en = translate(ref_value["label_fr"], _from="fr")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_en": value_en} })
            except KeyError:
                pass
    for tablename in DB.references.distinct("tablename"):
        for ref_value in DB[tablename].find({"$or":[{"label_fr": ""},{"label_fr": None}], "label_en":{"$nin": ["", None]}}, {"_id":1, "label_en":1}):
            try: 
                
                value_fr = translate(ref_value["label_en"], _from="en")
                DB[tablename].update_one({"_id": ref_value["_id"]}, {"$set": {"label_fr": value_fr} })
            except KeyError:
                pass
def create_default_users():
    default_users = [{
        "email": "constance.de-quatrebarbes@developpement-durable.gouv.fr", 
        "first_name": "Constance", 
        "last_name": "de Quatrebarbes", 
        "username": "c24b",
        "organization": "GD4H",
        "roles": ["admin", "expert"],
        "is_active": True, 
        "is_superuser": True,
        "lang": "fr"
    },{
        "email": "gd4h-catalogue@developpement-durable.gouv.fr", 
        "first_name": "GD4H", 
        "last_name": "Catalogue", 
        "username": "admin",
        "organization": "GD4H",
        "roles": ["admin", "expert"],
        "is_active": True, 
        "is_superuser": True,
        "lang": "fr"
    }]
    _id = DB.users.insert_many(default_users)
    create_logs("admin", action="create", perimeter="user",status=True, message="OK", scope=None, ref_id=_id.inserted_ids )
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB.users.aggregate(pipeline)
    # print(_id.inserted_ids)
    return _id.inserted_ids 

def create_comment(username, text="Ceci est un commentaire test"):
    default_user = DB.users.find_one({"username": username}, {"username": 1, "lang": 1})
    if default_user is None:
        raise Exception(username, "not found")
    default_lang = default_user["lang"]
    clean_text = bleach.linkify(bleach.clean(text))
    alternate_lang = SWITCH_LANGS[default_lang]
    alternate_text = translate(clean_text, _from=default_lang)
    comment = {"label_"+default_lang: clean_text, "label_"+alternate_lang: alternate_text, "date":datetime.datetime.now(), "user": default_user["username"]}
    return comment

def register_comment(comment, perimeter, scope, ref_id):
    comment["perimeter"] = perimeter
    comment["scope"] = scope #field
    comment["ref_id"] = ref_id
    DB.comments.insert_one(comment)
    


def create_logs(username, action, perimeter, status=True,  message="OK", scope=None, ref_id=None):
    default_user = DB.users.find_one({"username": username}, {"username":1})
    default_lang = "en"
    default_label = "label_en"
    ref_perimeter = DB["ref_perimeter"].find_one({default_label: perimeter}, {"_id":0} )
    ref_action = DB["ref_action"].find_one({default_label: perimeter}, {"_id":0})
    try:
        assert ref_perimeter is not None
    except AssertionError:
        raise ValueError(f"Log has no perimeter :'{perimeter}'")
        assert ref_action is not None
    except AssertionError:
        raise ValueError(f"Log has no action {perimeter}")
    return {
                "user": username,
                "action": action,
                "perimeter": perimeter,
                "scope": scope,
                "ref_id": ref_id, 
                "date": datetime.datetime.now(),
                "status": status,
                "message": message
            }

def init_data():
    DB.organizations.drop()
    import_organizations()
    DB.datasets.drop()
    import_datasets()
    # link_organizations_to_datasets()
    # register_comments()

if __name__=="__main__":
    init_data()