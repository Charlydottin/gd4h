#!/usr/bin/env python3

import itertools
import os
import datetime
import string
import bleach
from pymongo import MongoClient
from csv import DictReader, DictWriter
import json
from argostranslate import package, translate

# from pydantic import create_model 
# from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List
from itertools import groupby
import subprocess

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


def init_meta():
    DB.rules.drop()
    import_rules()
    DB.references.drop()
    import_references()
    

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
            print(row)

def import_references():
    ''' import_references() 
    from db.rules table 
    from data/references/ref_*.csv  
    - import each ref_table from csv into db tables
    - register each ref_table into table references
    - translate missing field with fr or en version
    - update ref_table csv files back again with db
    '''
    DB.references.drop()
    for ref_table in DB.rules.distinct("reference_table"):
        if ref_table != "":
            DB[ref_table].drop()
            print(f"Creating {ref_table} table")
            meta_reference = {"model":"reference"}
            meta_reference["table_name"] = ref_table
            meta_reference["slug"] =  ref_table.replace("ref_", "")
            ref_file =  os.path.join(data_dir, "references", ref_table+".csv")
            meta_reference["refs"] = [] 
            try:
                with open(ref_file, "r") as f:            
                    reader = DictReader(f, delimiter=",")
                    for row in reader:
                        clean_row = {k.strip(): v.strip() for k,v in row.items() if v is not None}
                        # print("translating missing values")
                        try:
                            if clean_row["name_en"] != "" and clean_row["name_fr"] == "":
                                clean_row["name_fr"] = translate(clean_row["name_en"], _from="en")
                            if clean_row["name_fr"] != "" and clean_row["name_en"] =="":
                                clean_row["name_en"] = translate(clean_row["name_fr"], _from="fr")
                        except KeyError:
                            pass
                        
                        if "root_uri" in clean_row:
                            meta_reference["root_uri"] = row["root_uri"]
                        if "root_uri" not in clean_row and "uri" in clean_row:
                            if clean_row["uri"] != "":
                                meta_reference["root_uri"] = "/".join(row["uri"].split("/")[:-1])
                        meta_reference["refs"].append(clean_row)            
                        try:
                            ref_id = DB[ref_table].insert_one(clean_row)
                        except pymongo.errors.DuplicateKeyError:
                            pass
                        del clean_row
                with open(ref_file, "w") as f:        
                    one_record = DB[ref_table].find_one({}, {"_id":0})
                    if one_record is not None:
                        fieldnames = list(one_record.keys())
                        writer = DictWriter(f, delimiter=",",fieldnames=fieldnames)
                        writer.writeheader()
                        for row in DB[ref_table].find({}, {"_id":0}):
                            writer.writerow(row)
                
                meta_reference["status"] = True
            except FileNotFoundError:
                print(f"Error! required reference {ref_table} has no corresponding file {ref_file}")
                meta_reference["status"] = False
            try:
                DB.references.insert_one(meta_reference)
            except pymongo.errors.DuplicateKeyError:
                print("Err")
                pass
    print("Created references table")
    

             
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

def get_references(field, lang="en"):
    '''get reference from given field name and lang'''
    if field.endswith("_fr"):
        lang = "fr"
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

           
def get_json_type(rule):
    datatype = {}
    if rule["constraint"] == "unique":
        datatype["unique"] = True
    elif rule["constraint"] == "if_exist":
        datatype["type"] =  [datatype["type"], "null"]
    if rule["datatype"] == "date":
        datatype["type"] = "string"
        datatype["format"] = "date-time"
        return datatype
    elif rule["datatype"] == "id":
        datatype["type"] = "string"    
        return datatype
    elif rule["datatype"] == "url":
        datatype["type"] = "string"
        datatype["format"] = "uri"
        datatype["pattern"] = "^https?://"
        return datatype
    elif rule["datatype"] == "object":
        datatype["$ref"] = f"#/definitions/{rule['slug'].title()}"
        return datatype
    else:
        datatype["type"] = rule["datatype"]
    return datatype

def get_json_ref_type(rule, ref_rule):
    datatype = {}
    if rule["model"] == "reference" and rule["slug"] in ["name_fr", "name_en", "uri"]:
        print(rule["field_id"], ref_rule["reference_table"])
        datatype["type"] = "string"
        datatype["enum"] = DB[ref_rule["reference_table"]].distinct(rule["slug"])
        if len(datatype["enum"]) == 0:
            del datatype["enum"]
        return datatype
    elif rule["model"] != "":
        if rule["datatype"] == "object":
            datatype["$ref"] = f"#/schemas/{rule['slug'].title()}.json"
            return datatype
    else:
        return get_json_type(rule)

def create_rules_json_schema():
    rule_model = create_model("Rules", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "rules.json"), "w") as f:
        f.write(rule_json_schema)

def create_reference_json_schema():
    rule_model = create_model("Reference", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(schema_dir, "references.json"), "w") as f:
        f.write(rule_json_schema)


def create_json_schema(model_name, model_name_title, model_rules, lang):
    if model_name not in DB.rules.distinct("model"):
        raise NameError("Model: {} doesn't exists".format(model_name))
    doc_root = { 
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": model_name_title,
        "type": "object",
        "description": f"A {model_name} in the catalog",
        "$id": f"http://gd4h.fr/schemas/{model_name}.json",
        "properties": {}
    }
    doc_root["properties"] = {}
    # doc_root["definitions"] = {name.title(): {} for name in DB.rules.distinct("modele") if name != model_name}
    for field in model_rules:
        
        doc_root["properties"][field["slug"]] = {
            "title": field[f"name_{lang}"].title(), 
            "description": field[f"description_{lang}"]    
            }       
        field_type = get_json_type(field)
        if field["multiple"]:
            doc_root["properties"][field["slug"]]["type"] = "array" 
            doc_root["properties"][field["slug"]]["items"] = get_json_type(field)

        else:
            doc_root["properties"][field["slug"]].update(field_type)
            # doc_root["properties"][field["slug"]].udpate(field_type)
    doc_root["definitions"]= { 
        field["slug"].title():{
            "properties": {
                # f["slug"]: get_json_type(f)
                f["slug"]: get_json_ref_type(f, field) 
                for f in get_rules(field["external_model"])
            }
        }  for field in model_rules if field["external_model"]!=""
    }
    doc_root["required"] = get_mandatory_fields(model_name)
            
                
    # validators = {
    # 'reference_validator':
    #     validator('username')(username_alphanumeric)
    # }
    # class Config:
    #     arbitrary_types_allowed = True
    
    with open(os.path.join(schema_dir, f"{model_name_title}.json"), "w") as f:
        data = json.dumps(doc_root, indent=4)
        f.write(data)
    return os.path.join(schema_dir, f"{model_name_title}.json")
    
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

def generate_model(input_file, output_file):
    # generate(input=input_file, input_file_type="jsonschema", field-constraints=True,use-generic-container-types=True, output="./organization.py")
    cmd = f"datamodel-codegen --input {input_file} --input-file-type jsonschema --field-constraints --enum-field-as-literal=one"
    python_model = subprocess.check_output(cmd.split(" "))
    with open(output_file, "wb") as f:
        f.write(python_model)
    # with os.listdir(schema_dir):
    print(python_model)
#         

if __name__ == '__main__':
    # import_rules()
    # import_references()
    for schema in create_json_schemas():
        input_file = schema
        model_name = input_file.split("/")[-1].split(".")[0]
        print(model_name)
        # output_file = os.path.join("back", "apps", model_name, "_model.py")
        generate_model(input_file, model_name+".py")
    # 
    # generate_model(input_file, output_file)