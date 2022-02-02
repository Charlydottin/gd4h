#!/usr/bin/env python3

import os
from pymongo import MongoClient
from csv import DictReader, DictWriter
import json
from argostranslate import package, translate

from pydantic import create_model 
from itertools import groupby
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
meta_dir = os.path.join(data_dir, "meta")
schema_dir = os.path.join(data_dir, "schemas")
dataset_dir = os.path.join(data_dir, "dataset")
organization_dir = os.path.join(data_dir, "organization")
model_dir = os.path.join(os.path.dirname(parent_dir), "back", "models")

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
                            print(clean_row.keys())
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
    return list(DB.rules.find({"model": model},{"_id":0}))

           
def get_json_type(rule):
    '''
    given key 'datatype' in rule record transform it into jsonschema datatype  
    given key 'constraint' in rule record add constraint
    '''
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
    ''' special case for external models 
    given rule 
    - if rule model is a reference and slug is name_fr or name_en or uri
    add enum validation and type
    - if rule model is an external model refer to external schema
    '''
    datatype = {}
    if rule["model"] == "reference" and rule["slug"] in ["name_fr", "name_en", "uri"]:
        if rule["slug"] == "uri":
            datatype["type"] = "string"
            datatype["format"] = "uri"
            datatype["pattern"] = "^https?://"
        else:
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

def create_json_schema_from_example(model):
    model_name = model.title()
    example = DB[model+"s"].find_one({"$nin": ["_id", "id"]}, {"_id":0})
    if example is not None:
        rule_model = create_model(model_name, **example)
        with open(os.path.join(data_dir, "schemas", f"{model_name}.json"), "w") as f:
            f.write(rule_model.schema_json())

def create_rules_json_schema():
    '''create json schema using example loaded into pydantic.create_model'''
    rule_model = create_model("Rules", **DB.rules.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(data_dir, "schemas", "rules.json"), "w") as f:
        f.write(rule_json_schema)
   

def create_reference_json_schema():
    '''create json schema using example loaded into pydantic.create_model'''
    rule_model = create_model("Reference", **DB.references.find_one({},{"_id":0}))
    rule_json_schema = rule_model.schema_json()
    with open(os.path.join(schema_dir, "references.json"), "w") as f:
        f.write(rule_json_schema)


def create_json_schema(model_name, model_name_title, model_rules, lang):
    '''Given rules for one model build a jsonschema dict'''
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
                           
    # with open(os.path.join(schema_dir, f"{model_name_title}.json"), "w") as f:
    #     data = json.dumps(doc_root, indent=4)
    #     f.write(data)
    # return os.path.join(schema_dir, f"{model_name_title}.json")
    return doc_root
def save_json_schema(model_name, json_data):
    '''savec generated json_schema into data/schema/'''
    json_filepath = os.path.join(schema_dir, f"{model_name.title()}.json")
    with open(json_filepath, "w") as f:
        data = json.dumps(json_data, indent=4)
        f.write(data)
    return json_filepath
def convert_jsonschema_to_openapi(model_name, json_data):
    return convert(json_data)


def create_json_schemas():
    '''from model list in rules 
    - generate json_schema
    - import pydantic_model
    '''
    models = {}
    for model_name in DB.distinct("model"):
        model_rules = get_rules(model_name)
        is_multilang_model = any([r["translation"] for r in model_rules])
        
        if is_multilang_model:
            for lang in AVAILABLE_LANG:
                model_name_title = model_name.title()+ lang.upper()
                
                json_schema = create_json_schema(model_name, model_name_title, model_rules, lang)
                save_json_schema(model_name, json_schema)
                py_model = create_model(model_name.title(), **json_schema)
                models[model_name+"_"+lang] = py_model
                # model_py = create_model(model_name_title, **json_schema)
                
                # yield create_json_schema(model_name, model_name_title, model_rules, lang)

    else:
        model_name_title = model_name.title()
        json_schema = create_json_schema(model_name, model_name_title, model_rules, lang="fr")
        model_py = create_model(model_name_title, **json_schema)
        save_json_schema(model_name, json_schema)
        models[model_name+"_"+lang] = py_model
        yield(model_name_title, model_py)

# def write_model_py_file(model_name, json_schema):
#     '''using datamodel-codegenerator transform json-schema into a pydantic model.py'''
#     json_file_input = Path(save_json_schema(model_name, json_schema))
#     model_output = os.path.join(curr_dir,"models", f"{model_name}.py")
#     open(model_output, 'a').close()
#     pymodel =generate(
#             json_schema,
#             input_file_type="jsonschema", 
#             field_constraints = True,
#             enum_field_as_literal="one",
            
#     )
#     print(pymodel)
#     model: str = pymodel.read_text()
#     print(model)
#     return model
# def generate_model(model_name, json_schema):
#     '''using datamodel-codegenerator CLI to transform json-schema into a pydantic <model_name>.py'''
#     json_file_input = save_json_schema(model_name, json_schema)
#     model_output = os.path.join(curr_dir,"models", f"{model_name}.py")
#     # pymodel = generate(
#     #     json_schema,
#     #     input_file_type="jsonschema", 
#     #     field_constraints=True, 
#     #     use_generic_container_types=True, 
#     #     output=model_output)
#     # model: str = pymodel.read_text()
#     # print(model)

#     cmd = f"datamodel-codegen --input={json_file_input} --input-file-type=jsonschema --field-constraints --enum-field-as-literal=one"
#     try:
#         python_model = subprocess.check_output(cmd.split(" "),shell=True,stderr=subprocess.STDOUT)
#         with open(model_output, "wb") as f:
#             f.write(python_model)
#         return model_output.read_text()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == '__main__':
    import_rules()
    import_references()
    