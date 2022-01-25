#!/usr/bin/env python3
import os
import datetime
import bleach
from pymongo import MongoClient
from csv import reader, writer, DictReader, DictWriter
from copy import copy
from argostranslate import package, translate

curr_dir = os.getcwd()
# print(curr_dir)
parent = os.path.dirname(os.getcwd())
data_dir = os.path.join(curr_dir, "data")
print(data_dir)
metadata_doc = os.path.abspath(os.path.join(data_dir, "meta", "rules.csv"))
reference_doc = os.path.abspath(os.path.join(data_dir, "meta", "references_tables.csv"))


DATABASE_NAME = "GD4H_V1"
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
    import_organizations_from_csv()
    DB.datasets.drop()
    import_dataset_from_csv()
    link_organizations_to_datasets()
    register_comments_from_datasets()

def init_meta():
    DB.meta_fields.drop()
    create_meta_fields()
    DB.meta_references.drop()
    DB.references.drop()
    create_references()
    create_ref_tables()
    DB.logs.drop()
    DB.users.drop()
    create_default_users()
    translate_fr_references()
    translate_en_references()

def translate(text, _from="fr"):
    if _from == "fr":
        return fr_en.translate(text)
    else:
        return en_fr.translate(text)
    

def create_meta_fields():
    coll_name = "meta_fields"
    DB[coll_name].drop()
    print(f"Creating {coll_name}")
    with open(metadata_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            if row["slug"] == "":
                break
            else:
                for k,v in row.items():
                    if v == "True":
                        row[k] = True
                    if v == "False":
                        row[k] = False
                
                # print(row["slug"], row["translation"], row["multiple"], row["is_controled"])            
            _id = DB[coll_name].insert_one(row).inserted_id
    # print(DB[coll_name].find_one({"slug":"acronym", "model": "Dataset"}))
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB[coll_name].aggregate(pipeline)

def create_references():        
    coll_name = "references"
    DB[coll_name].drop()
    print(f"Creating {coll_name}")
    with open(reference_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            print(row)
            if row["tablename"] == "":
                break
            row["tablename"] = "ref_"+ row["fieldname"]
            _id = DB[coll_name].insert_one(row).inserted_id
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB[coll_name].aggregate(pipeline)
            
def create_ref_tables():
    print(f"Creating meta_references")
    for ref in DB["references"].find({}, {"_id":0}):
        ref_file =  os.path.join(data_dir, "references", ref["tablename"]+".csv")
        coll_name = ref["tablename"]
        DB[coll_name].drop()
        print(f"Creating {coll_name}")
        try:
            with open(ref_file, "r") as f:
                reader = DictReader(f, delimiter=",")
                for row in reader:
                    _id = DB[coll_name].insert_one({k.strip(): v.strip() for k,v in row.items() if v is not None}).inserted_id
                    # print(_id)
        except FileNotFoundError:
            DB["references"].update_one({"fieldname":ref["fieldname"]}, {"$set":{"status": False, "msg": "No corresponding file references found"}})
            CENSUS_DB = mongodb_client["census"]
            values = CENSUS_DB.datasets.distinct(ref["fieldname"])
            for v in values:
                _id = DB[coll_name].insert_one({"label_fr":v, "label_en": None, "uri": None}).inserted_id
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB["references"].aggregate(pipeline)
            
    errors = DB["references"].find({"status": False})
    for e in errors:
        print("Error", e)

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
    # pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    # DB["comments"].aggregate(pipeline)



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

def create_license():
    for license_name in DB.ref_license_name.distinct("license_name"): 
        print(license_name)
    # for licence_n in DB.datasets.distinct("license_name"):
    #     if licence_n != "" and licence_n is not None:
    #         print(licence_n)
    #         match = DB.datasets.find_one({"license_name":licence_n}, {"license_name":1, "license_type": 1, "is_opensource":1, "_id":0})
    #         name = licence_n
    #         ltype = [DB.ref_license_type.find_one({"label_fr": n}, {"_id":0, "slug":1}) for n in match["license_type"]]
    #         is_opendata = match["is_opensource"]
    #         DB.licenses.insert_one({"name":name, "type": ltype, "is_opendata": is_opendata})
        # if licence_n != "" and licence_n is not None:
        #     for l in CENSUS_DB.datasets.find({"license_name":licence_n}, {"license_type": 1, "is_opensource":1}):
                
        #         if license_name is not None:
        #             license = { 
        #                 "name": license_name,
        #                 "type":[DB.ref_license_type.find_one({"label_fr":n}, {"_id":0}) for n in l["license_type"]], 
        #                 "is_opendata":l["is_opensource"]
        #             }
        #             if DB.licenses.find_one({"name.0.label_fr": licence_n}) is None:
                        # DB.licenses.insert_one(license)                
                
def import_organizations_from_csv():
    print("Create Organizations")
    org_doc = os.path.abspath(os.path.join(data_dir, "organizations", "census_organizations.csv"))
    with open(org_doc, "r") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            agent_type = row["agent_type_uri"]
            row["agent_type"] = DB.ref_agent_type.find_one({"uri":agent_type})
            del row["agent_type_uri"]
            org_type = row["organization_type"]
            row["organization_type"] = DB.ref_organization_type.find_one({"label_fr":org_type})
            if row["organization_type"] is None:
                DB.ref_organization_type.insert_one({"label_fr": org_type, "label_en": translate(org_type)})
                row["organization_type"] = DB.ref_organization_type.find_one({"label_fr":org_type})
            org = DB.organizations.insert_one(row)
            create_logs("admin","create", "organization", True, "OK", scope=None, ref_id=org.inserted_id)
    pipeline = [ {'$project': {"id": {'$toString': "$_id"}, "_id": 0,"value": 1}}]
    DB.organizations.aggregate(pipeline)

def get_field_rule(model, slug):
    correspondancy_value_rule = {
        "contact_comments":"contact_type_comments",
        "spatial_geographical_coverage": "geographical_geospatial_coverage",
        "is_opensource": "is_opendata",
    }
    rule = DB.meta_fields.find_one({"model": model, "slug":slug}, {"_id":0, "model":0})
    if rule is not None:
        return slug, rule
    else:
        try:
            new_slug = correspondancy_value_rule[slug]
            new_rule = DB.meta_fields.find_one({"model": model, "slug":new_slug}, {"_id":0, "model":0})
            if new_rule is not None:
                return new_slug, new_rule
        except KeyError:
            pass
    return slug, None

def get_field_slugs_for_model(model="Dataset"):
    return sorted([n["slug"]for n in DB.meta_fields.find({"model": model}, {"_id":0, "slug":1})])


def format_value_with_declared_datatype(rule, value):
    if rule["datatype"] == "str":
        if value == "":
            return None
        try:
            assert isinstance(value, str)
            return value
        except AssertionError:
            return str(value)
                            
    elif rule["datatype"] == "bool":
        try:
            assert isinstance(value, bool)
            return value
        except AssertionError:
            return bool(value)

    elif rule["datatype"] == "int":
        try:
            assert isinstance(value, int)
        except AssertionError:
            try:
                return int(value)
            except ValueError:
                return None

    else:
        if value == "":
            return None        
        else:
            return value

def reference_table_exists(reference_table):
    if DB[reference_table].count_documents({}) > 0:
        return DB[reference_table]["status"]
    else:
        return False   

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

def import_dataset_from_csv():
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
    
def register_comments_from_datasets():
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
    
    # labels = [f"label_{l}" for l in AVAILABLE_LANG]
    # print(labels)
    # last_log = DB.logs.find_one({"perimeter":"dataset", "action":{"$in": ["create"]}}, sort=[("date", pymongo.DESCENDING)])
    # last_user = DB.users.find_one({"username":last_log["user"]})
    
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
if __name__ == '__main__':
    init_meta()
    init_data()
    print(DATABASE_NAME, "is_ready")