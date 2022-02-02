#!/usr/bin/env python3.9
# file: generate_ref_models

import os
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader, select_autoescape

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
tpl_dir = os.path.join(data_dir, "templates")
model_dir = os.path.join(data_dir, "models")



# todo: use settings
DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]
AVAILABLE_LANG = ["fr","en"]



env = Environment(loader=FileSystemLoader(tpl_dir), autoescape=select_autoescape())

def get_references():
    '''from rules table get all the external references that consists of an enumeration of choice'''
    references = {}
    #[{"ref_name": {"key": {"en": "x", "fr":'y'}, key2: }
    for rule in DB.rules.find({"constraint": "enum", "is_controled":True, "reference_table": {"$ne": ""}}):
        ref_name =rule["reference_table"]
        ref_model_name = rule["reference_table"].replace("ref_", "").title()
        references[ref_model_name] = []
        
        for record in DB[ref_name].find({}):
            references[ref_model_name].append({"en": record["name_en"], "fr": record["name_fr"]})
            
    return references

def generate_references_model():
    template = env.get_template('references_model.tpl')
    references_filename = "references.py"
    with open(os.path.join(model_dir, references_filename), "w") as f:
        py_file = template.render(available_lang = AVAILABLE_LANG, references=get_references(), model=[get_model("reference")])
        f.write(py_file)

def get_pydantic_datatype(datatype):
    if datatype == "string":
        return 'str'
    if datatype == "id":
        return 'str'
    if datatype =="boolean":
        return 'bool'
    if datatype == 'date':
        return 'datetime'
    if datatype == "url":
        return 'HttpUrl'
    if datatype == 'object':
        return 'dict'
def generate_model(model_name):
    template = env.get_template('model.tpl')
    references_filename = f"{model_name}.py"
    with open(os.path.join(model_dir, references_filename), "w") as f:
        py_file = template.render(models=get_model(model_name), langs = AVAILABLE_LANG)
        f.write(py_file)

def get_model(model):
    model_info = []
    external_refs = []
    external_models = [] 
    # external_models = [n["external_model"] for n in DB["rules"].find({"model": model, "external_model":{"$nin": ["", "reference"]}}, {"_id":0}) if n["slug"]!= "_id" and n["slug"]!= "id"]
    # model_info.append(("import_model", list(set(external_models))))
    # external_references = [n["slug"] for n in DB["rules"].find({"model": model, "reference_table":{"$ne": ""}, "is_controled":True}, {"_id":0}) if n["slug"]!= "_id" and n["slug"]!= "id"]
    model_info.append(("import_reference", list(set(external_refs))))
    model_rules = list([n for n in DB["rules"].find({"model": model}, {"_id":0}) if n["slug"]!= "_id" and n["slug"]!= "id"])
    info = {}
    is_multilang_model = any([r["translation"] for r in model_rules])
    if is_multilang_model:
        for lang in AVAILABLE_LANG:
            model_name = model.title()+lang.title()
            info[model_name] = []
            for rule in model_rules:
                field_name = rule["slug"]
                py_type = get_pydantic_datatype(rule['datatype'])
                if rule["multiple"]:
                    if py_type == "dict":
                        if rule["reference_table"] != "":
                            if rule["is_controled"]:
                                py_type = rule["reference_table"].replace("ref_", "").title()+"Enum"+lang.title()
                                external_refs.append(("references", py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}] = [{py_type}.option_1]"
                            else:
                                py_type = 'str'
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                            
                        elif rule["external_model"] != "":
                            external_model_rules = list(DB.rules.find({"model": rule["external_model"]}, {"_id":0, "translation":1}))
                            is_multilang_ext_model = any([r["translation"] for r in external_model_rules])
                            if is_multilang_ext_model:
                                py_type = rule["external_model"].title()+lang.title()
                                external_models.append((rule["external_model"], py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                            else:
                                py_type = rule["external_model"].title()
                                external_models.append((rule["external_model"], py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                    else:
                        if rule["mandatory"] is False:
                            line = f"{field_name}: List[{py_type}] = []"
                        else:
                            line = f"{field_name}: List[{py_type}]"
                else:
                    if py_type == "dict":
                        if rule["reference_table"] != "":
                            if rule["is_controled"]:
                                py_type = rule["reference_table"].replace("ref_", "").title()+"Enum"+lang.title()
                                external_refs.append(("references", py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                            else:
                                py_type = 'str'
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                            
                        elif rule["external_model"] != "":
                            external_model_rules = [DB.rules.find({"model": rule["external_model"]})]
                            is_multilang_ext_model = any([r["translation"] for r in external_model_rules])
                            if is_multilang_ext_model:
                                py_type = rule["external_model"].title()+lang.title()
                                external_models.append((rule["external_model"], py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                            else:
                                py_type = rule["external_model"].title()
                                external_models.append((rule["external_model"], py_type))
                                if rule["mandatory"] is False:
                                    line = f"{field_name}: List[{py_type}] = []"
                                else:
                                    line = f"{field_name}: List[{py_type}]"
                    else:
                        if rule["mandatory"] is False:
                            line = f"{field_name}: Optional[{py_type}] = None"
                        else:
                            line = f"{field_name}: {py_type}"
                info[model_name].append(line)
    else:
        model_name = model.title()
        info[model_name] = []
        for rule in model_rules:
            field_name = rule["slug"]
            py_type = get_pydantic_datatype(rule['datatype'])
            if rule["multiple"]:
                if py_type == "dict":
                    if rule["reference_table"] != "":
                        if rule["is_controled"]:
                            py_type = rule["reference_table"].replace("ref_", "").title()+"Enum"
                            external_refs.append(("references", py_type))
                            if rule["mandatory"] is False:
                                line = f"{field_name}: List[{py_type}] = []"
                            else:
                                line = f"{field_name}: List[{py_type}]"
                        else:
                            py_type = 'str'
                            if rule["mandatory"] is False:
                                line = f"{field_name}: List[{py_type}] = []"
                            else:
                                line = f"{field_name}: List[{py_type}]"
                            
                    elif rule["external_model"] != "":
                        py_type = rule["external_model"].title()
                        external_models.append((rule["external_model"], py_type))
                        if rule["mandatory"] is False:
                            line = f"{field_name}: List[{py_type}] = []"
                        else:
                            line = f"{field_name}: List[{py_type}]"
                if rule["mandatory"] is False:
                    line = f"{field_name}: List[{py_type}] = []"
                else:
                    line = f"{field_name}: List[{py_type}]"
            else:
                if rule["mandatory"] is False:
                    line = f"{field_name}: Optional[{py_type}] = None"
                else:
                    line = f"{field_name}: {py_type}"
            info[model_name].append(line)
    print("import_model", external_models)
    print("import_references", external_refs)
    model_info.append(("import_model", list(set(external_models))))
    model_info.append(("import_reference", list(set(external_refs))))
    model_info.extend(list(info.items()))
    return model_info

def get_models():
    models = {}
    for model_name in DB.rules.distinct("model"):
        model_d = get_model(model_name)
        models.update(model_d)
    return models

def generate_models():
    template = env.get_template('models.tpl')
    references_filename = "models.py"
    with open(os.path.join(model_dir, references_filename), "w") as f:
        py_file = template.render(available_lang = AVAILABLE_LANG, references=get_references(), models=get_models())
        f.write(py_file)

if __name__ == "__main__":
    for model in DB.rules.distinct("model"):
        if model == "reference":
            generate_references_model()
        else:
            generate_model(model)
    