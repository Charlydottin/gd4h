from fastapi import APIRouter, Body, Request, HTTPException, status, Query
from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from elasticsearch7 import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match
from pymongo import MongoClient

# from .models import Query
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

es = Elasticsearch("http://localhost:9200")
# DATABASE_NAME = "GD4H_V1"
# mongodb_client = MongoClient("mongodb://localhost:27017")
# DB = mongodb_client[DATABASE_NAME]

router = APIRouter()



@router.get("/datasets/{lang}", response_description="Search Full Text in name, description, data section( environment, nature, subthematic, exposure_factor, exp")
async def search_datasets(lang:str, q: Optional[str] = Query(None, min_length=2, max_length=50)):
    # fields = [
    #     d["slug"] for d in 
    #     DB.meta_fields.find({"model":"Dataset", "external_model":{"$nin":["Comment", "Organization"]}, "is_indexed":True}, {"_id":0, "slug":1})
    #     ]
    fields = ['name', 'acronym', 'description', 'environment', 'nature', 'subthematic', 'exposure_factor', 'exposure_factor_category', 'theme_category', "organization"]
    index_name = f"datasets_{lang}"
    tokens = q.strip().split()
    
    final_query = {
        "multi_match" : {
        "query":    q, 
        "fields": fields
        }
    }

    # if len(tokens) > 1:
        #very restrictive query
        # must = [] 
        # for t in tokens:
        #     must.append({ "term": { "text": t }})
        # final_q = {"bool": {"must": must}}
        #comprehensive query
        # should = [] 
        # for t in tokens:
        #     should.append({ "term": { "text": t }})
        # final_q = {"bool": {"should": should}}
        #exact match
        # final_q= {
        # "match" : {
        # "terms":    q, 
        # "fields": fields
        #     }
        
    highlight = {
        
        "pre_tags" : "<em class='tag-fr highlight'>",
        "post_tags" :"</em>",
        "fields" : {f:{} for f in fields }
        }
    res = es.search(index=index_name, query=final_query, highlight=highlight)
    result_count =  res["hits"]["total"]["value"]
    results = []
    for r in res["hits"]["hits"]:
        result = r["_source"]
        result["_id"] = r["_id"]
        result["score"] = str(round(r["_score"]*10,2))+"%"
        result["highlight"] = r["highlight"]
        results.append(result)
    return {"results":results, "count": result_count}
    

# @router.get("/datasets/{lang}/filter", response_description="search by facet")
# async def filter_datasets(lang:str, q: Optional[List[str]] = Query(None), request=Request):
#     facets = []
#     for doc in await request.app.mongodb["meta_fields"].find({"is_indexed": True}, {"slug":1,"label_fr":1,"label_en":1, "translation":1, "type":1, "multiple":1}).to_list(length=200):
#         facets.append(doc)