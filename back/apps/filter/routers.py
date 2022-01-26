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


# @router.get("/datasets/{key}/{value}/{lang}", response_description="Filter dataset by value")
# async def filter_datasets(request: Request, lang:str, key:str, value:str):    
#     doc = request.app.mongodb["meta_fields"].find_one({"slug": key})
#     if doc["translation"] is True:
#         search_key = { key+'.label_'+lang: value }
#     else:
#         search_key = { key: value }
#     datasets = []
#     for doc in await request.app.mongodb["datasets"].find(search_key, {"_id":0}).to_list(length=100):
#         datasets.append(doc)
#     return {"datasets": datasets}
    

# @router.get("/organizations/{key}/{value}/{lang}", response_description="Filter organization by value")
# async def search_datasets(request: Request, lang:str, key:str, value:str):    
#     doc = request.app.mongodb["meta_fields"].find_one({"slug": key})
#     if doc["translation"] is True:
#         search_key = { key+'.label_'+lang: value }
#     else:
#         search_key = { key: value }
#     datasets = []
#     for doc in await request.app.mongodb["datasets"].find(search_key, {"_id":0}).to_list(length=100):
#         datasets.append(doc)
#     return {"organizations": datasets}

            
# @router.get("/{filter}/{lang}", response_description="Filter dataset")
# async def get_filter_values(filter:str, lang:str, request: Request):
#     rule = request.app.mongodb["meta_fields"].find_one({"slug": filter})
#     refs = []
#     if rule["reference_table"] != "":
#         for rf in await request.app.mongodb[rule["reference_table"]].distinct("label_"+lang):
#             refs.append(rf)
#         return {"values": refs}
#     return {"values": refs}

@router.get("/rules/", response_description="Get rules")
async def get_rules(rule: str, request: Request):
    facets = []
    for doc in await request.app.mongodb["meta_fields"].find({}, {"_id":0}).to_list(length=200):
        facets.append(doc)
    return {"data": facets}


@router.get("/rules/{slug}", response_description="Get rule for field")
async def get_rules(slug: str, request: Request):
    facets = []
    for doc in await request.app.mongodb["meta_fields"].find({"slug": slug}, {"_id":0}).to_list(length=200):
        facets.append(doc)
    return {"data": facets}


@router.get("/facet/", response_description="Get facet field")
async def get_facet_fields(request: Request):
    facets = []
    for doc in await request.app.mongodb["meta_fields"].find({"is_facet": True}, {"slug":1,"label_fr":1,"label_en":1, "translation":1, "type":1, "multiple":1}).to_list(length=200):
        facets.append(doc)
    return {"data": facets}

@router.get("/index/", response_description="Get indexed values")
async def get_index_fields(request: Request):
    facets = []
    for doc in await request.app.mongodb["meta_fields"].find({"is_indexed": True}, {"slug":1,"label_fr":1,"label_en":1, "translation":1, "type":1, "multiple":1}).to_list(length=200):
        facets.append(doc)
    return {"data": facets}




