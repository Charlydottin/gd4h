#!/usr/bin/.venv/python3


from pymongo import MongoClient
from elasticsearch7 import Elasticsearch
import datetime

es = Elasticsearch("http://localhost:9200")

DATABASE_NAME = "GD4H_V1"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]

def create_mapping(lang="fr"):
    map_property = {}
    if lang == "fr":
        analyzer = "std_french"
    else:
        analyzer = "std_english"
    for rules in DB.meta_fields.find({"model":"Dataset", "external_model":{"$ne":"Comment"}, "$or":[{"is_indexed":True}, {"is_facet":True}]}, {"_id":0}):
        if rules["translation"]:
            prop_key = rules["slug"]+"_"+lang
        else:
            prop_key = rules["slug"]
        if rules["datatype"] in ["str", "dict"]:
            map_property[prop_key] = {"type": "text"}
            map_property[prop_key]["fields"] = {"raw": {"type": "keyword"}}
            map_property[prop_key]["analyzer"] = analyzer
            
            
        elif rules["datatype"] == "date":
            map_property[prop_key] = {"type": "date", "format": "strict_date_optional_time_nanos"}
        elif rules["datatype"] == "bool":
            map_property[prop_key]= {"type":"boolean"}
        else:
            pass
    return map_property

def create_index(index_name="datasets", lang="fr"):
    # if lang="fr":
    settings = {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "std_english": {
                        "type": "standard",
                        "stopwords": "_english_"
                        },
                        "std_french": {
                        "filters": [
                            "standard",
                            "lowercase",
                            "french_ellision",
                            "icu_folding"
                        ],
                        "type": "custom",
                        "stopwords": "_french_",
                        "tokenizer": "icu_tokenizer"
                        }
                    }
                }            
    }
    config = {"settings": settings, "mappings": {"properties":create_mapping(lang)}}
    mappings = {"properties": create_mapping(lang)}
    index_name = f"{index_name}_{lang}"
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = es.indices.create(index=index_name, settings=config["settings"], mappings=config["mappings"], ignore=400)
    print(i)
    
def map_document(doc, translated_fields, other_fields, lang="fr"):
    label = "label_"+lang
    doc_id = str(doc["_id"])
    index_doc = {}
    for k in doc.keys():
        if k == "organizations":
            index_doc[k] = [n.get("name") for n in doc[k]]
        elif "last_" in k:
            index_doc[k] = doc[k]
        elif k in translated_fields:
            try:
                index_doc[k] = doc[k].get("label_"+lang)
            except: 
                index_doc[k] = [n.get("label_"+lang) for n in doc[k]]
        elif k in other_fields:
            index_doc[k] = doc[k]
        else:
            pass
    return (doc_id, doc)

def index_datasets(lang="fr"):
    index_name = f"datasets_{lang}"
    fields = ["_id"]
    translated_fields = [rules["slug"] for rules in DB.meta_fields.find({"model":"Dataset", "external_model":{"$ne":"Comment"},"translation":True, "$or":[{"is_indexed":True}, {"is_facet":True}]}, {"_id":0, "slug":1})]
    other_fields = [rules["slug"] for rules in DB.meta_fields.find({"model":"Dataset", "external_model":{"$ne":"Comment"},"translation":False, "$or":[{"is_indexed":True}, {"is_facet":True}]}, {"_id":0, "slug":1})]
    fields = {k:1 for k in fields+translated_fields+other_fields}
    label = "label_"+lang
    for doc in DB.datasets.find({}, fields):
        doc_id = str(doc["_id"])
        print(doc_id)
        del doc["_id"]
        index_doc = {}
        for k in doc.keys():
            if k == "organizations":
                index_doc[k] = [n.get("name") for n in doc[k]]
            elif "last_" in k:
                pass
            elif k in translated_fields:
                try:
                    index_doc[k] = doc[k].get("label_"+lang)
                except: 
                    index_doc[k] = [n.get("label_"+lang) for n in doc[k]]
            elif k in other_fields:
                index_doc[k] = doc[k]
            else:
                pass
        response = es.index(index = index_name,id = doc_id, document = index_doc,request_timeout=45)
        print(response)
        
if __name__ == "__main__":
    create_index()
    create_index("en")
    index_datasets()
    index_datasets("en")