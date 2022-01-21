from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from elasticsearch import Elasticsearch
# from elasticsearch_dsl import Search
# from elasticsearch_dsl.query import MultiMatch, Match, Query as Q
# from elasticsearch_dsl import Document, Date, Integer, Keyword, Text

import os

db_elastic = {
    'host': os.getenv("ES_HOST"),
    'user': os.getenv("ES_USER"),
    'password': os.getenv("ES_PASSWORD"),
    'database': os.getenv("ES_DB"),
    'port': os.getenv("ES_PORT")
}

es = Elasticsearch(**db_elastic)

router = APIRouter()

# "integration_status", "translation" : false, "multiple" : false }
# "slug" : "state", "translation" : false, "multiple" : false }
# "last_inserted", "translation" : false, "multiple" : false }
# "last_modification", "translation" : false, "multiple" : false }
# "organizations", "translation" : false, "multiple" : true }
# "dataset_type", "translation" : true, "multiple" : false }
# "environment", "translation" : true, "multiple" : true }
# "nature", "translation" : true, "multiple" : false }
# "subthematic", "translation" : true, "multiple" : false }
# "exposure_factor", "translation" : true, "multiple" : true }
# "exposure_factor_category", "translation" : true, "multiple" : true }
# "theme_category", "translation" : true, "multiple" : false }
# "is_opendata", "translation" : false, "multiple" : false }
# "license_name", "translation" : true, "multiple" : false }
# "license_type", "translation" : true, "multiple" : true }
# "has_restrictions", "translation" : false, "multiple" : false }
# "has_pricing", "translation" : false, "multiple" : false }
# "has_compliance", "translation" : false, "multiple" : false }
# "data_format", "translation" : false, "multiple" : true }
# "data_domain", "translation" : true, "multiple" : false }


@router.get("/datasets/{key}/{value}/{lang}", response_description="Filter dataset by value")
async def filter_datasets(request: Request, lang:str, key:str, value:str):    
    doc = request.app.mongodb["meta_fields"].find_one({"slug": key})
    if doc["translation"] is True:
        search_key = { key+'.label_'+lang: value }
    else:
        search_key = { key: value }
    datasets = []
    for doc in await request.app.mongodb["datasets"].find(search_key, {"_id":0}).to_list(length=100):
        datasets.append(doc)
    return {"datasets": datasets}
    

@router.get("/organizations/{key}/{value}/{lang}", response_description="Filter organization by value")
async def search_datasets(request: Request, lang:str, key:str, value:str):    
    doc = request.app.mongodb["meta_fields"].find_one({"slug": key})
    if doc["translation"] is True:
        search_key = { key+'.label_'+lang: value }
    else:
        search_key = { key: value }
    datasets = []
    for doc in await request.app.mongodb["datasets"].find(search_key, {"_id":0}).to_list(length=100):
        datasets.append(doc)
    return {"organizations": datasets}

            
@router.get("/{filter}/{lang}", response_description="Filter dataset")
async def get_filter_values(filter:str, lang:str, request: Request):
    rule = request.app.mongodb["meta_fields"].find_one({"slug": filter})
    refs = []
    if rule["reference_table"] != "":
        for rf in await request.app.mongodb[rule["reference_table"]].distinct("label_"+lang):
            refs.append(rf)
        return {"values": refs}
    return {"values": refs}





