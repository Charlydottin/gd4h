from pymongo import MongoClient
from elasticsearch7 import Elasticsearch
import datetime
# import settings

es = Elasticsearch("http://localhost:9200")
DATABASE_NAME = "GD4H_V2"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]
#put into settings
LANGS = ["fr", "en"]

def get_indexed_and_facet_fields(model="dataset"):
    return list(DB.rules.find({"model":model, "$or":[{"is_indexed":True}, {"is_facet":True}]}, {"_id":0}))

def create_mapping(model="dataset", lang="fr"):
    map_property = {}
    if lang == "fr":
        analyzer = "std_french"
    else:
        analyzer = "std_english"
    for rules in get_indexed_and_facet_fields(model):
        prop_key = rules["slug"]
        if rules["datatype"] == "object":
            # if rules["external_model"] != "":
            map_property[prop_key] = {"type": "nested"} 
        elif rules["datatype"] == ["string", "url", "email", "str"]:
            map_property[prop_key] = {"type": "text"}
            map_property[prop_key]["fields"] = {"raw": {"type": "keyword"}}
            map_property[prop_key]["analyzer"] = analyzer 
        elif rules["datatype"] == "date":
            if rules["constraint"] == "range":
                map_property[prop_key]= {"type":"integer_date"}
            else:
                map_property[prop_key] = {"type": "date", "format": "strict_date_optional_time_nanos"}
        elif rules["datatype"] == "boolean":
            map_property[prop_key]= {"type":"boolean"}
        elif rules["datatype"] in ["number", "integer", "int"]:
            if rules["constraint"] == "range":
                map_property[prop_key]= {"type":"integer_range"}
            else:    
                map_property[prop_key]= {"type":"integer"}
        else:
            map_property[prop_key]= {"type":rules["datatype"]}
    return map_property

def create_index(model="dataset", lang="fr"):
    # if lang="fr":
    settings = {
                "number_of_shards": 2,
                "number_of_replicas": 1,
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
    config = {"settings": settings, "mappings": {"properties":create_mapping(model, lang)}}
    mappings = {"properties": create_mapping(lang)}
    index_name = f"{model}_{lang}"
    es.indices.delete(index=index_name, ignore=[400, 404])
    i = es.indices.create(index=index_name, settings=config["settings"], mappings=config["mappings"], ignore=400)
    print(i)
    return
    
def map_document(doc, translated_fields, other_fields, lang="fr"):
    label = "label_"+lang
    doc_id = str(doc["_id"])
    index_doc = {}
    for k in doc.keys():
        if k == "organizations":
            index_doc[k] = [{l:m for l,m in n.items if n!="_id"} for n in doc[k]]
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

def index_documents(model="dataset", lang="fr"):
    index_name = f"{model}_{lang}"
    col_name = f"{model}s"
    fields = get_indexed_and_facet_fields(model)
    fields.append("_id")
    display_fields = {f:1 for f in fields}
    for doc in DB[col_name].find({}, display_fields):
        doc_id = str(doc["_id"])
        index_doc = doc[lang]
        index_doc["_id"] = doc_id
        response = es.index(index = index_name,id = doc_id, document = index_doc,request_timeout=45)
        print(response)
        
def index_document(model, doc):
    for lang in LANGS:
        index_name = f"{model}_{lang}"
        fields = get_indexed_and_facet_fields(model)
        fields.append("_id")
        doc_id = str(doc["_id"])
        index_doc = doc[lang]
        index_doc["_id"] = doc_id
        response = es.index(index = index_name,id = doc_id, document = index_doc,request_timeout=45)
        print(response)