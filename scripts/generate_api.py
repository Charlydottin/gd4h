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

def get_model_names(model_name):
    models = []
    is_multilang_model = any([r["translation"] for r in DB["rules"].find({"model":model_name}, {"translation": 1, "_id":0})])
    if is_multilang_model:
        for lang in AVAILABLE_LANG:
            models.append((model_name, lang, model_name.title()+lang.title()))
    else:
        models.append((model_name, "", model_name.title()))
    return models
def list_model_names():
    '''get list of model_names'''
    models = []
    for model_name in DB["rules"].distinct("model"):
        models.extend(get_model_names(model_name))
    models.append(["rule", "", "Rules"])
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



def get_rule_model():
    example = DB.rules.find_one()
    model = ["Rule", []]
    for key, value in example.items():
        if key == "_id":
            line = f"{key}: str"
        if key == "external_model_displaykeys":
            line = f"{key}: List[str] = []"
        else:
            py_type = type(value).__name__
            
            line = f"{key}: {py_type} = None"
        model[1].append(line)
    return [model]

def get_filter_model(model_name="dataset"):
    model_info = []
    external_refs = []
    external_models = [] 
    info = {}
    model_rules = list(DB["rules"].find({"model": model_name, "is_facet":True}, {"_id":0}))
    for lang in AVAILABLE_LANG:
        model_title = "Filter"+model_name.title()+lang.title()
        info[model_title] = []
        for rule in model_rules:
            field_name = rule["slug"]
            py_type = get_pydantic_datatype(rule['datatype'])
            if rule["multiple"]:
                if rule["reference_table"] != "":
                    py_type = rule["reference_table"].replace("ref_", "").title()+"Enum"+lang.title()
                    external_refs.append(("reference", py_type))
                    line = f"{field_name}: List[{py_type}] = [{py_type}.option_1]"
                elif rule["external_model"] != "":
                    external_model_rules = list(DB.rules.find({"model": rule["external_model"]}, {"_id":0, "translation":1}))
                    is_multilang_ext_model = any([r["translation"] for r in external_model_rules])
                    if is_multilang_ext_model:
                        py_type = rule["external_model"].title()+lang.title()
                        external_models.append((rule["external_model"], py_type))
                        line = f"{field_name}: List[{py_type}] = []"
                    else:
                        py_type = rule["external_model"].title()
                        external_models.append((rule["external_model"], py_type))
                        line = f"{field_name}: List[{py_type}] = []"
                else:
                    line = f"{field_name}: List[{py_type}] = []"
            else:
                if rule["reference_table"] != "":
                    py_type = rule["reference_table"].replace("ref_", "").title()+"Enum"+lang.title()
                    external_refs.append(("reference", py_type))
                    line = f"{field_name}: List[{py_type}] = [{py_type}.option_1]"   
                elif rule["external_model"] != "":
                    external_model_rules = [DB.rules.find({"model": rule["external_model"]})]
                    is_multilang_ext_model = any([r["translation"] for r in external_model_rules])
                    if is_multilang_ext_model:
                        py_type = rule["external_model"].title()+lang.title()
                        external_models.append((rule["external_model"], py_type))
                        line = f"{field_name}: {py_type} = None"
                    else:
                        py_type = rule["external_model"].title()
                        external_models.append((rule["external_model"], py_type))
                        line = f"{field_name}: {py_type} = None"
                else:
                    line = f"{field_name}: Optional[{py_type}] = None"
            info[model_title].append(line)
    
    external_models = set([n for n in external_models])
    model_info.append(("import_model", list(external_models)))
    model_info.append(("import_reference", list(set(external_refs))))
    model_info.extend(list(info.items()))
    if len(external_models) > 0:
        model_info.append(("update_model", info.keys()))
    return model_info

def get_model(model_name="dataset"):
    model_info = []
    external_refs = []
    external_models = [] 
    info = {}
    model_rules = list(DB["rules"].find({"model": model_name}, {"_id":0}))
    is_multilang_model = any([r["translation"] for r in model_rules])
    if is_multilang_model:
        for lang in AVAILABLE_LANG:
            model_title = model_name.title()+lang.title()
            info[model_title] = []
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
                info[model_title].append(line)
    else:
        model_title = model_name.title()
        info[model_title] = []
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
            info[model_title].append(line)
    external_models = set([n for n in external_models if n[0]!= model_name and n[0]!= "reference"])
    model_info.append(("import_model", list(external_models)))
    model_info.append(("import_reference", list(set(external_refs))))
    model_info.extend(list(info.items()))
    
    if len(external_models) > 0:
        model_info.append(("update_model", info.keys()))
    return model_info
    
def generate_model(models, output_file):
    template = env.get_template('model.tpl')
    with open(output_file, "w") as f:
        py_file = template.render(models=models, langs = AVAILABLE_LANG)
        f.write(py_file)

def generate_main(output_file):
    template = env.get_template('main.tpl')
    with open(output_file, "w") as f:        
        py_file = template.render(route_models=list_model_names(), langs = AVAILABLE_LANG)
        f.write(py_file)

def generate_router(route_models, output_file):
    template = env.get_template('routers.tpl')
    with open(output_file, "w") as f:
        py_file = template.render(route_models=route_models)
        f.write(py_file)

def generate_app(back_name="test_back"):
    back_dir = os.path.join(parent_dir, back_name)
    apps_dir = os.path.join(back_dir, "apps")
    if not os.path.exists(back_dir):
        os.makedirs(back_dir)
    if not os.path.exists(apps_dir):
        os.makedirs(apps_dir)
    print("Creating app")
    model_list = DB.rules.distinct("model")+["rule"]
    for model_name in model_list:    
        print(f"creating {model_name}")
        model_dir = os.path.join(apps_dir, model_name)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        model_file = os.path.join(model_dir, "models.py")
        if model_name == "reference":
            generate_references_model(model_file)
        elif model_name == "rule":
            models = get_rule_model()
            generate_model(models, model_file)
        else:
            models = get_model(model_name)
            generate_model(models, model_file)

        router_file = os.path.join(model_dir, "routers.py")
        if model_name == "rule":
            route_models = [('Rule', '', 'rule')]
        else:
            route_models= get_model_names(model_name)
        print(route_models)
        generate_router(route_models, router_file)
        init_file = os.path.join(model_dir, "__init__.py")
        Path(init_file).touch()
        continue
    main_file = os.path.join(back_dir, "main.py")
    generate_main(main_file)
    print("Writing main")
    init_file = os.path.join(back_dir, "__init__.py")
    Path(init_file).touch()
    print(f"sucessfully generated app in {back_dir}")
    print(f"Run\ncd {back_dir}\nuvicorn main:app --reload")

def get_indexed_fields():
    return [n["slug"] for n in get_rules("dataset") if n["is_indexed"]]

def get_filter_fields():
    return [n["slug"] for n in get_rules("dataset") if n["is_facet"]]

def get_filters():
    facet_rules = [n for n in get_rules("dataset") if n["is_facet"]]
    filters = []
    for facet in facet_rules:
        field_name = facet["slug"]  
        is_controled, is_multiple, is_bool = facet["is_controled"], facet["multiple"], facet["datatype"] == "boolean"
        filter_d = {
            "name": field_name, 
            "is_controled":is_controled, 
            "is_multiple":is_multiple, 
            "is_bool": is_bool,
            "values_fr":[],
            "values_en":[],
        }
        if is_controled:
            filter_d["values_en"] = DB[facet["reference_table"]].distinct("name_en")
            filter_d["values_fr"] = DB[facet["reference_table"]].distinct("name_fr")
        elif is_bool:
            filter_d["values_en"] = ["Oui", "Non"]
            filter_d["values_en"] = ["Yes", "No"]
        filters.append(filter_d)

if __name__ == "__main__":
    # generate_app()
    models = get_filter_model("dataset")
    generate_model(models, "filter.py")