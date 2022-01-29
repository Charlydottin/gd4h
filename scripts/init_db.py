#!/usr/bin/env python3
from asyncore import write
import enum
from gettext import translation
import itertools
import os
import datetime
from termios import BSDLY
import bleach
from pymongo import MongoClient
from csv import reader, writer, DictReader, DictWriter
from copy import copy
import json
from argostranslate import package, translate
from pydantic import create_model 
from typing import Optional, List
from itertools import groupby
from bson.objectid import ObjectId as BsonObjectId
import pymongo

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
meta_dir = os.path.join(data_dir, "meta")

dataset_dir = os.path.join(data_dir, "dataset")
organization_dir = os.path.join(data_dir, "organization")


DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]

AVAILABLE_LANG = ["fr","en"]
SWITCH_LANGS = dict(zip(AVAILABLE_LANG,AVAILABLE_LANG[::-1]))

installed_languages = translate.get_installed_languages()
fr_en = installed_languages[1].get_translation(installed_languages[0])
en_fr = installed_languages[0].get_translation(installed_languages[1])

def init():
    init_meta()
    init_data()

def init_data():
    DB.organizations.drop()
    import_organizations()
    DB.datasets.drop()
    import_dataset()
    link_organizations()
    register_comments()

def init_meta():
    DB.rules.drop()
    import_rules()
    DB.references.drop()
    import_references()
    DB.logs.drop()
    DB.users.drop()
    create_default_users()
    # translate_fr_references()
    # translate_en_references()


def translate(text, _from="fr"):
    if _from == "fr":
        return fr_en.translate(text)
    else:
        return en_fr.translate(text)
    

def import_rules():
    coll_name = "rules"
    DB[coll_name].drop()
    rules_doc = os.path.join(meta_dir,"rules.csv")
    print(f"Creating {coll_name} table")
    with open(rules_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            if row["slug"] == "":
                break
            else:
                for k,v in row.items():
                    if k == "external_model_display_keys":
                        row[k] == v.split("|")
                    elif v == "True":
                        row[k] = True
                    elif v == "False":
                        row[k] = False
                    else:
                        try:
                            row[k] = int(v)
                        except ValueError:
                            row[k] = str(v)
            _id = DB[coll_name].insert_one(row).inserted_id
            

def import_references():
    ''' Import references and each ref_table into db tables
    translate missing field fr or en 

    '''
    reference = {"model": "reference"}
    for ref_table in DB.rules.distinct("reference_table"):
        print(ref_table)
        if ref_table != "":
            DB[ref_table].drop()
            print(f"Creating {ref_table} table")
            reference["table_name"] = ref_table
            reference["field_slug"] =  ref_table.replace("ref_", "")
            ref_file =  os.path.join(data_dir, "references", ref_table+".csv")
            refs = [] 
            try:
                with open(ref_file, "r") as f:
                    
                    reader = DictReader(f, delimiter=",")
                    for row in reader:
                        clean_row = {k.strip(): v.strip() for k,v in row.items() if v is not None}
                        print("translating missing values")
                        try:
                            if clean_row["name_en"] != "" and clean_row["name_fr"] == "":
                                clean_row["name_fr"] = translate(clean_row["name_en"], _from="en")
                            if clean_row["name_fr"] != "" and clean_row["name_en"] =="":
                                clean_row["name_en"] = translate(clean_row["name_fr"], _from="fr")
                        except KeyError:
                            pass
                        
                        if "root_uri" in clean_row:
                            reference["root_uri"] = row["root_uri"]
                        if "root_uri" not in clean_row and "uri" in clean_row:
                            if clean_row["uri"] != "":
                                reference["root_uri"] = "/".join(row["uri"].split("/")[:-1])
                        refs.append(row)            
                        try:
                            ref_id = DB[ref_table].insert_one(clean_row)
                        except pymongo.errors.DuplicateKeyError:
                            pass
                with open(ref_file, "w") as f:        
                    one_record = DB[ref_table].find_one({}, {"_id":0})
                    if one_record is not None:
                        fieldnames = list(one_record.keys())
                        print(fieldnames)
                        writer = DictWriter(f, delimiter=",",fieldnames=fieldnames)
                        writer.writeheader()
                        for row in DB[ref_table].find({}, {"_id":0}):
                            writer.writerow(row)
                reference["references"] = refs
                reference["status"] = True
            except FileNotFoundError:
                print(f"Error! required reference {ref_table} has no corresponding file {ref_file}")
                reference["status"] = False
            try:
                DB.references.insert_one(reference)
            except pymongo.errors.DuplicateKeyError:
                pass
            

    print("Created references table")
    

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

             
def get_not_translated_fields(model="organization"):
    fields = DB.rules.find({"model": model, "translation": False}, {"slug":1})
    return [f["slug"] for f in fields]
def get_translated_fields(model="organization"):
    fields = DB.rules.find({"model": model, "translation": True}, {"slug":1, "is_controled": 1, "reference_table":1})
    # for f in fields:
    #     if f["is_controled"]:
    #         DB[f["reference_table"]].distinct()
    return [f["slug"] for f in fields]

def get_rule(model, field_slug):
    rule = DB.rules.find_one({"model": model, "slug": field_slug})
    return rule

def import_organizations():
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
            create_logs("admin","create", "organization", True, "OK", scope=None, ref_id=db_org.inserted_id)
    print(DB.organizations.count_documents({}), "organization inserted")




def find_reference_by_label_fr(reference_table, value):
    external_ref = DB[reference_table].find_one({"label_fr": value})
    if external_ref is not None:
        external_ref["_ref"] = reference_table
        return True, external_ref
    else:
        error_msg = "ERROR: reference value '{}' not found in '{}' as 'label_fr'".format(value, reference_table)
        return False, error_msg
def find_reference_by_label_en(reference_table, value):
    external_ref = DB[reference_table].find_one({"label_en": value})
    if external_ref is not None:
        external_ref["_ref"] = reference_table
        return True, external_ref
    else:
        error_msg = "ERROR: reference value '{}' not found in '{}' as 'label_en'".format(value, reference_table)
        return False, error_msg


def import_datasets():
    print("Create Datasets")
    created_datasets = []
    datasets_doc = os.path.abspath(os.path.join(data_dir, "datasets", "census_datasets_fr.csv"))
    with open(datasets_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            dataset = {}
            #COMMON
            dataset["name"] = row["dataset_name"]
            dataset["acronym"] = row["acronym"]
            dataset["description"] = {"label_fr":row["description"], "label_en": None}
            dataset["organizations"] = [{"name":n.strip()} for n in row["organization"].split("|")]
            dataset["url"] = row["link"]
            #CONTACT
            dataset["contact"] = [row["contact"]]
            dataset["contact_type"] = [{"label_fr": "email", "label_en": "email"}]
            dataset["contact_comments"] = [create_comment("admin", text=row["contact"])]
            # SANTE-ENVIRONNEMENT
            dataset["data_domain"] = {"label_fr": row["data_domain"], "label_en": None}
            dataset["theme_category"] = {"label_fr":row["theme_category"], "label_en": None}
            dataset["thematic_field"] = {"label_fr":row["thematic_field"], "label_en": None} 
            dataset["nature"] = {"label_fr":row["nature"], "label_en": None}
            dataset["environment"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["environment"].split("/")]
            dataset["subthematic"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["subthematic"].split("/")]
            dataset["exposure_factor_category"] = [{"label_fr":n.strip(), "label_en": translate(n.strip())} for n in row["exposure_factor_category"].split("/")]
            # this a simple copy for NOW
            dataset["exposure_factor"] = dataset["exposure_factor_category"]
            # TECH
            dataset["has_filter"] = bool(row["filter"])
            dataset["has_search_engine"] = bool(row["search_engine"])
            dataset["has_missing_data"] = bool(row['missing_data']!= "" and row['missing_data'] is not None and row["missing_data"] != "None")
            if dataset["has_missing_data"]: 
                dataset["missing_data_comments"] = [create_comment("admin", text=row["missing_data"])]
            dataset["has_documentation"] = bool(row['documentation']!= "" and row['documentation'] is not None and row["documentation"] != "None")
            if dataset["has_documentation"]: 
                dataset["documentation_comments"] = [create_comment("admin", text=row["documentation"])]
            
            dataset["is_downloadable"] = bool(row["downloadable"])
            dataset["broadcast_mode"] = [ {"label_fr":n.strip(), "label_en":None} for n in row["broadcast_mode"].split("/") ]
            dataset["files_format"] = [n.strip().title() for n in row["format"].split("/")]
            dataset["tech_comments"] = []
            # dataset["tech_comments"] = [create_comment("c24b", text="Commentaire sur l'accès technique")]
            #LEGAL
            dataset["license_name"] = {"label_fr":row["license_name"], "label_en": None}
            dataset["license_type"] = [{"label_fr":n, "label_en": n} for n in row["license_type"].split("/")]
            dataset["has_pricing"] = bool(row['pricing']!= "Gratuit")
            if row['pricing']!= "Gratuit":

                dataset["legal_comments"] = [
                    create_comment("c24b", text=row["pricing"])]
            else:
                dataset["legal_comments"] = []
            dataset["has_restriction"] = bool(row['restrictions']!= "")
            if dataset["has_restriction"]: 
                dataset["restrictions_comments"] = [create_comment("admin", text=row["restrictions"])]
            dataset["has_compliance"] = bool(row['compliance']!= "")
            if dataset["has_compliance"]: 
                dataset["compliance_comments"] = [create_comment("admin", text=row["compliance"])]
            #GEO
            dataset["is_geospatial_data"] = bool(row["geospatial_data"])
            if dataset["is_geospatial_data"]:
                dataset["administrative_territory_coverage"] = [n.strip() for n in row["administrative_territory_coverage"].split(",")]
                dataset["geospatial_geographical_coverage"] = row["geographical_geospatial_coverage"].split("+")
                dataset["geographical_information_level"] = [{"label_fr":v.strip(), "label_en":translate(v.strip())} for v in row["geographical_information_level"].split("/")]
                dataset["projection_system"] = [n.strip() for n in row["projection_system"].split("/")]
                dataset["related_geographical_information"] = bool(row["related_geographical_information"] == "")
            if row["related_geographical_information"] != "":
                dataset["geo_comments"] = [create_comment("c24b", text=row["related_geographical_information"])]
            else:
                dataset["geo_comments"] = []
            #TIME
            dataset["year"] = [n.strip() for n in row["year"].split("-")]
            dataset["temporal_scale"] = [v.strip() for v in row["temporal_scale"].split("/")]
            dataset["update_frequency"] = {"label_fr":row["update_frequency"], "label_en": translate(row["update_frequency"])}
            if row["automatic_update"] == "false":
                dataset["automatic_update"] = False
            if row["automatic_update"] == "true":
                dataset["automatic_update"] = False
            if row["automatic_update"] == "":
                dataset["automatic_update"] = None
            # ADMIN
            dataset["last_updated"] = row["last_updated"]
            dataset["last_inserted"]= row["last_inserted"]
            dataset["last_modification"] = row["last_modification"]
            dataset["related_referentials"] = [v.strip() for v in row["related_referentials"].split("|")]
            dataset["other_access_points"] = [v.strip() for v in row["other_access_points"].split("|")]
            # dataset["context_comments"] = [create_comment("admin", text="Commentaire sur le contexte de production du dataset")]
            dataset["context_comments"] = []
            dataset["comments"] = [create_comment("admin", text=row["comment"])]
            ds = DB.datasets.insert_one(dataset)
            created_datasets.append(ds.inserted_id)
    for id in created_datasets:
        DB.logs.insert_one(create_logs("admin", "create", "dataset", True, "OK", scope=None, ref_id=id))
           
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

def return_type_example(datatype):
    if datatype == "dict":
        return "object", {}
    elif datatype == "bool":
        return "boolean", False
    elif datatype == "id":
        return "string", "61f39f8a701f929ed50e61be" 
    elif datatype == "int":
        return "number", 1
    elif datatype == "date":
        return "date", "2017-01-01"
    else:
        return "string", ""
def gen_json_item(rule, lang="fr"):
    
    field_json = {
                    "name": rule["slug"],
                    "title": rule["label_"+lang],
                    "description": rule["description_"+lang], 
                }
    str_datatype, example = return_type_example(rule["datatype"])
    if rule["multiple"]:
        field_json["type"] = "array"
        field_json["items"] = {"type": str_datatype}
        field_json["example"] = [example]
    else: 
        field_json["type"] = str_datatype
        field_json["example"] = example    
    if rule["mandatory"]:
        field_json["constraints"] = {"required": True}
    
    if rule["reference_table"] != "":
        enum_values = DB[rule["reference_table"]].distinct("label_"+lang)
        if "constraints" in field_json:
            field_json["constraints"]["enum"] = enum_values
        else:
            field_json["constraints"] = {
                "enum": enum_values            
            }
    if rule["constraint"] == "unique":
        if "constraints" in field_json:
            field_json["constraints"]["unique"] = True
        else:
            field_json["constraints"] = {
                "unique": True            
            }
    
    # if rule["external_model"] != "":
    #     field_json["type"] = [
    #                     "object",{"$ref":"https://github.com/c24b/gd4h/catalogue/raw/v0.0.1/{}-schema.json".format(rule["external_model"])}
    #     ]
    return field_json
def create_json_m_simple():
    
    {
        "title": "{dataset_model}",
        "type": "object",
        "properties": {
        }
    }
    property_item = { "title": "{Model}",
            "default": "dataset",
            "type": "string"}
def create_json_model():
    '''generate JSON empty file from rules table'''
    rules = [rule for rule in DB["rules"].find({},{})]
    

    final_models = {}
    for  model_name, field_rules in itertools.groupby(rules, key=lambda x:x["model"]):
        print(model_name)
        field_rules = list(field_rules)
        is_multilang_model = any([r["translation"] for r in field_rules])
        if is_multilang_model:
            for lang in AVAILABLE_LANG:
                root_schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": f"{model_name}_{lang}",
                "title": "{} - {}".format(model_name.title(), lang),
                "description": f"Spécification du modèle de données {model_name} relatif au catalogue des jeux de données Santé Environnement du GD4H",
                "contributors": [
                    {
                    "title": "GD4H",
                    "role": "author"
                    },
                    {
                    "title": "Constance de Quatrebarbes",
                    "role": "contributor"
                    }
                ],
                "version": "0.0.1",
                "created": "2022-01-28",
                "lastModified": "2022-01-28",
                "homepage": "https://github.com/c24b/gd4h/",
                "$id": f"{model_name}_{lang}-schema.json",
                "path": f"https://github.com/c24b/gd4h/catalogue/raw/v0.0.1/{model_name}_{lang}-schema.json",
                "type":object,
                "properties":[

                ]
                }
                for rule in field_rules:
                    root_schema["properties"].append(gen_json_item(rule, lang))
                yield root_schema
                root_schema["properties"] = []
        else:
            root_schema = {
                "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
                "name": f"{model_name}",
                "title": f"{model_name.title()} Simplifié",
                "description": f"Spécification du modèle de données {model_name.title()} relatif au catalogue des jeux de données Santé Environnement du GD4H",
                "contributors": [
                    {
                    "title": "GD4H",
                    "role": "author"
                    },
                    {
                    "title": "Constance de Quatrebarbes",
                    "role": "contributor"
                    }
                ],
                "$id": f"{model_name}-schema.json",
                "version": "0.0.1",
                "created": "2022-01-28",
                "lastModified": "2022-01-28",
                "homepage": "https://github.com/c24b/gd4h/",
                "path": f"https://github.com/c24b/gd4h/catalogue/raw/v0.0.1/{model_name}-schema.json".format(model_name),
                "properties":[

                ]
            }
            for rule in field_rules:
                root_schema["properties"].append(gen_json_item(rule, "en"))
            yield root_schema
    
def write_json_model():
    for json_schema in create_json_model():
        with open(os.path.join(data_dir, "schemas", json_schema["$id"]), "w") as f:
            f.write(json.dumps(json_schema, indent=4))
            print(json_schema["$id"], "ready!")

def create_json_rules_model():
    rule_model = create_model("Rules", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "rules.json"), "w") as f:
        f.write(rule_json_schema)

def create_models():
    class Config:
        arbitrary_types_allowed = True

    # ModelWithPath = create_model(
    #     "ModelWithPath", path=(request.param, ...), __config__=Config
    # )
    pass
if __name__ == '__main__':
    import_rules()
    import_references()
    # create_json_rules_model()