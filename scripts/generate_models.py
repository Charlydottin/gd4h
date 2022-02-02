#!/usr/bin/env python3.9
# file: generate_ref_models

from mimetypes import init
import os
from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)
data_dir = os.path.join(parent_dir, "data")
tpl_dir = os.path.join(data_dir, "templates")
# model_dir = os.path.join(data_dir, "models")
model_dir = os.path.join(parent_dir, "new_back")
apps_dir = os.path.join(model_dir, "apps")
# todo: use settings
DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]
AVAILABLE_LANG = ["fr","en"]


env = Environment(loader=FileSystemLoader(tpl_dir), autoescape=select_autoescape())

def get_rule(model, field_slug):
    '''get rule for given model and given field'''
    rule = DB.rules.find_one({"model": model, "slug": field_slug})
    return rule

def get_rules(model):
    '''get rule for given model and given field'''
    return list(DB.rules.find({"model": model},{"_id":0}))

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

def get_references_details():
    references = {}
    for ref in DB.references.find({}, {"_id":0}):
        ref_name = ref["slug"]
        table_name = ref["table_name"]
        model_fr = ref_name+"EnumFr"
        model_en = ref_name+"EnumEn"
        rules = DB.rules.find_one({"reference_table":ref["table_name"]})
        values_fr = [n["name_fr"] for n in ref["refs"]]
        values_en = [n["name_en"] for n in ref["refs"]]
        references[ref_name] = {
            "table_name": table_name, 
            "name_fr":model_fr, 
            "name_en":model_en,
            "is_controled": rules["is_controled"],
            "is_multiple": rules["multiple"],
            "is_facet": rules["is_facet"],
            "is_indexed": rules["is_indexed"],
            "values_fr": values_fr,
            "values_en": values_fr
        }
    return references

def list_model_names():
    '''get list of model_names'''
    models = []
    for model_name in DB["rules"].distinct("model"):
        if model_name != "reference":
            is_multilang_model = any([r["translation"] for r in DB["rules"].find({"model":model_name}, {"translation": 1, "_id":0})])
            if is_multilang_model:
                for lang in AVAILABLE_LANG:
                    models.append((model_name, model_name.title()+lang.title()))
            else:
                models.append((model_name, model_name.title()))
    return models

def list_ref_names():
    '''get list of referenceEnum names'''
    refs = []
    for ref_name in DB["references"].distinct("slug"):
        refs.append(ref_name.title()+"EnumFr")
        refs.append(ref_name.title()+"EnumEn")
    return refs

def get_import(model_name):
    imports = list(set([r["external_model"] for r in get_rules(model_name)]))
    return(model_name, imports)

def solve_circular_import():
    circular_import = []
    for model in DB.rules.distinct("model"):
        model, imports = get_import(model)
        print(model)
        print(imports)

def generate_references_model(output_file):
    template = env.get_template('references_model.tpl')
    with open(output_file, "w") as f:
        py_file = template.render(available_lang = AVAILABLE_LANG, references=get_references(), model=[get_model("reference")])
        f.write(py_file)

def get_pydantic_datatype(datatype):
    '''transform rules datatype into pydantic datatype'''
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
    if datatype == "email":
        return 'EmailStr'
    if datatype == 'object':
        return 'dict'

def get_model_names(model_name):
    models = []
    is_multilang_model = any([r["translation"] for r in DB["rules"].find({"model":model_name}, {"translation": 1, "_id":0})])
    if is_multilang_model:
        for lang in AVAILABLE_LANG:
            models.append((model_name, model_name.title()+lang.title()))
    else:
        models.append((model_name, model_name.title()))
    return models

def get_model(model):
    model_info = []
    external_refs = []
    external_models = [] 
    info = {}
    model_rules = list([n for n in DB["rules"].find({"model": model}, {"_id":0}) if n["slug"]!= "_id" and n["slug"]!= "id"])
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
                                external_refs.append(("reference", py_type))
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
                                external_refs.append(("reference", py_type))
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
                            external_refs.append(("reference", py_type))
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
    external_models = [n for n in external_models if n[0]!= model and n[0]!= "reference"]
    model_info.append(("import_reference", list(set(external_refs))))
    model_info.extend(list(info.items()))
    model_info.append(("import_model", list(set(external_models))))
    return model_info

def generate_model(model_name, output_file):
    template = env.get_template('model.tpl')
    with open(output_file, "w") as f:
        py_file = template.render(models=get_model(model_name), langs = AVAILABLE_LANG)
        f.write(py_file)

def generate_main(output_file):
    template = env.get_template('main.tpl')
    with open(output_file, "w") as f:
        
        py_file = template.render(route_models=list_model_names(), langs = AVAILABLE_LANG)
        f.write(py_file)

def generate_router(model, output_file):
    template = env.get_template('routers.tpl')
    with open(output_file, "w") as f:
        py_file = template.render(route_models=get_model_names(model), langs = AVAILABLE_LANG)
        f.write(py_file)
    pass

def generate_app():
    back_dir = os.path.join(parent_dir, "test_back")
    apps_dir = os.path.join(back_dir, "apps")
    if not os.path.exists(back_dir):
        os.makedirs(back_dir)
    if not os.path.exists(apps_dir):
        os.makedirs(apps_dir)
    
    main_file = os.path.join(back_dir, "main.py")
    generate_main(main_file)
    init_file = os.path.join(back_dir, "__init__.py")
    Path(init_file).touch()
    for model in DB.rules.distinct("model"):    
        if model == "reference":
            model_dir = os.path.join(apps_dir, model)
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            model_file = os.path.join(model_dir, "models.py")
            generate_references_model(model_file)
            router_file = os.path.join(model_dir, "routers.py")
            generate_router(model, router_file)
            init_file = os.path.join(model_dir, "__init__.py")
            Path(init_file).touch()
        else:
            model_dir = os.path.join(apps_dir, model)
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            output_file = os.path.join(model_dir, "models.py")
            generate_model(model, output_file)
            router_file = os.path.join(model_dir, "routers.py")
            generate_router(model, router_file)
            init_file = os.path.join(model_dir, "__init__.py")
            Path(init_file).touch()

if __name__ == "__main__":
    generate_app()
    