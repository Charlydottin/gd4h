#!/usr/bin/env python3
from asyncore import write
import enum
from gettext import translation
import itertools
import os
import datetime
from termios import BSDLY
from textwrap import indent
from xml.parsers.expat import model
import bleach
from pymongo import MongoClient
from csv import reader, writer, DictReader, DictWriter
from copy import copy
import json
from argostranslate import package, translate
from pydantic import create_model 
from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List
from itertools import groupby
from bson.objectid import ObjectId as BsonObjectId
import pymongo

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
meta_dir = os.path.join(data_dir, "meta")
schema_dir = os.path.join(data_dir, "schemas")
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
    link_dataset2organizations()
    register_comments()

def init_meta():
    DB.rules.drop()
    import_rules()
    DB.references.drop()
    import_references()
    # DB.logs.drop()
    # DB.users.drop()
    # create_default_users()
    

def translate(text, _from="fr"):
    if _from == "fr":
        return fr_en.translate(text)
    else:
        return en_fr.translate(text)
    

def import_rules():
    '''
    import_rules() from data/meta/rules.csv
    '''
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
                    # if row["multiple"] == "True":
                    if "|" in v:
                        row[k] == v.split("|")
                    elif k == "external_model_display_keys":
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
    ''' import_references() 
    from db.rules table 
    from data/references/ref_*.csv  
    - import each ref_table from csv into db tables
    - register each ref_table into table references
    - translate missing field with fr or en version
    - update ref_table csv files back again with db
    '''
    reference = {"model": "reference"}
    for ref_table in DB.rules.distinct("reference_table"):
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
    rules = DB.rules.find({"model": model},{"_id":0})
    return list(rules)

def get_references(field, lang="fr"):
    '''get reference from given field name and lang'''
    return DB["ref_"+field].distinct(f"name_{lang}")
    

def get_reference_list(model, field_slug,lang="fr"):
    rule = get_rule(model, field_slug)
    display_key = rule["external_model_display_keys"][0]
    if rule["translation"]:
        key = "".join([display_key,"_", lang])
    else:
        key = display_key
    references = DB[rule["reference_table"]].distinct(display_key)
    return references

           

def get_json_type_format(rule):
    print(rule["field"], rule["reference_table"], rule["external_model"])
    if rule["datatype"] == "date":
        datatype = { "type": "string", "format": "date-time" }
    elif rule["datatype"] == "id":
        datatype =  { "type": "string"}
    elif rule["datatype"] == "url":
        datatype = { "type": "string", "format": "uri", "pattern": "^https?://" }
    elif rule["datatype"] == "dict":
        datatype = {"type": "object"}
    else:
        datatype = {"type": rule["datatype"]}
    if rule["constraint"] == "oneOf":
        print(rule["field"], rule["reference_table"], rule["external_model"])
        # if rule["slug"].endswith("_fr"):    
        #     values = get_references(rule["external_model"], lang="fr")
        # else:
        #     values = get_references(rule["slug"], lang="fr")
        datatype["enum"] = []
        # datatype["enum"] = values
    elif rule["constraint"] == "unique":
        datatype["unique"] = True
    elif rule["constraint"] == "if_exist":
        datatype["type"] =  [datatype["type"], "null"]
    return datatype



def create_rules_json_schema():
    rule_model = create_model("Rules", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "rules.json"), "w") as f:
        f.write(rule_json_schema)

def create_reference_json_schema():
    rule_model = create_model("Reference", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "rules.json"), "w") as f:
        f.write(rule_json_schema)


def create_json_schema(model_name, model_name_title, model_rules, lang):
    doc_root = { 
        "title": model_name_title,
        "type": "object",
        "$id": f"http://gd4h.fr/schemas/{model_name}.json",
        "properties": {}
    }
    doc_root["required"] =  []
    doc_root["properties"] = {}
    doc_root["definitions"] = {name.title(): {} for name in DB.rules.distinct("modele") if name != model_name}
    doc_root["required"] = get_mandatory_fields(model_name)
    for field in model_rules:
        doc_root["properties"][field["slug"]] = {
            "title": field[f"name_{lang}"].title(), 
            "description": field[f"description_{lang}"]    
            }   
        if field["external_model"] != "":
            ref_model = field['external_model']
            if field["reference_table"] != "":
                def_name = f"#/definitions/Reference{ref_model.title()}"
            else:
                def_name = f"#/definitions/{ref_model.title()}"
            reference_rules = get_rules(ref_model)
            reference_model = {r["slug"]: get_json_type_format(r) for r in reference_rules}
            required = get_mandatory_fields(ref_model)
            doc_root["definitions"][def_name] = {
                "properties": reference_model, 
                "required": required
            }
        
        if field["multiple"]:
            doc_root["properties"][field["slug"]] = {"type": "array"}
            if field["external_model"] != "":
                ref_model = field['external_model']
                if field["reference_table"] != "":
                    def_name = f"#/definitions/Reference{ref_model.title()}"
                else:
                    def_name = f"#/definitions/{ref_model.title()}"
                    
            doc_root["properties"][field["slug"]]["items"] = {
                "$ref": def_name, 
                }
            
        else:
            if field["external_model"] != "":
                if field["reference_table"] != "":
                    doc_root["properties"][field["slug"]]["items"] = {
                        "$ref": f"#/definitions/Reference{field['slug'].title()}"
                        
                        }
                else:
                    doc_root["properties"][field["slug"]]["items"] = {"$ref": f"#/definitions/{field['external_model'].title()}"}
            else:
                doc_root["properties"][field["slug"]].update(convert2json_schema_type(field["datatype"]))


        
            
    # validators = {
    # 'reference_validator':
    #     validator('username')(username_alphanumeric)
    # }
    # class Config:
    #     arbitrary_types_allowed = True
    
    with open(os.path.join([schema_dir, f"{model_name_title}.json"]), "w") as f:
        data = json.dumps(doc_root, indent=4)
        f.write(data)
    return os.path.join([schema_dir, f"{model_name_title}.json"])
    
def create_json_schemas():
    rules = list(DB.rules.find({},{"_id":0}))
    for model_name, field_rules in itertools.groupby(rules, key=lambda x:x["model"]):
        model_rules = list(field_rules)
    #     is_multilang_model = any([r["translation"] for r in model_rules])
    #     if is_multilang_model:
    #         for lang in AVAILABLE_LANG:
    #             model_name_title = model_name.title()+ lang.upper()
    #             create_model2jsonschema(model_name, model_name_title, model_rules, lang)

    # else:
        model_name_title = model_name.title()
        yield create_json_schema(model_name, model_name_title, model_rules, lang="fr")

def generate_models():
    with os.listdir(schema_dir):

#     datamodel-codegen --input Organization.json --input-file-type jsonschema --field-constraints --use-generic-container-types    

if __name__ == '__main__':
    import_rules()
    import_references()
    create_json_schemas()