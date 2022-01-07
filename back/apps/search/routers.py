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

@router.get("/datasets/{lang}", response_description="Search Full Text in title and description")
async def search_datasets(request: Request, lang="fr"):    
    final_q = {"query":{"bool": { "should": {"terms":"description.label_"+lang, "terms": "title"}}}}
    res = es.search(index="gd4h_datasets", query=final_q)
    return {"datasets": [r["_id"] for r in res["hits"]["hits"]],"count":len(res["hits"]["hits"])}
    

@router.get("/organizations/{lang}", response_description="Search Full Text in title and description")
async def search_datasets(request: Request, lang="fr"):    
    final_q = {"query":{"bool": { "should": {"terms": "name.label_"+{lang}, "terms":"acronym.label_"+lang}}}}
    res = es.search(index="gd4h_datasets", query=final_q)
    return {"datasets": [r["_id"] for r in res["hits"]["hits"]],"count":len(res["hits"]["hits"])}

            
            


