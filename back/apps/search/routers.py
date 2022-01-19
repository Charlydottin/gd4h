from fastapi import APIRouter, Body, Request, HTTPException, status, Query
from typing import Optional
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
DATABASE_NAME = "GD4H_V1"
mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client[DATABASE_NAME]

router = APIRouter()

@router.get("/")
async def get_results(q: Optional[str] = Query(None, min_length=3, max_length=50)):
    print(q)
    return {"query":q}

@router.get("/datasets/{lang}", response_description="Search Full Text in description")
async def search_datasets(lang:str, q: Optional[str] = Query(None, min_length=3, max_length=50)):
    # fields = [
    #     d["slug"] for d in 
    #     DB.meta_fields.find({"model":"Dataset", "external_model":{"$nin":["Comment", "Organization"]}, "is_indexed":True}, {"_id":0, "slug":1})
    #     ]
    fields = ["_id", 'name', 'acronym', 'description', 'environment', 'nature', 'subthematic', 'exposure_factor', 'exposure_factor_category', 'theme_category']
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
        
    highlight = {
        
        "pre_tags" : ["<em class='tag-fr'>", "<em>"],
        "post_tags" : ["</em>", "</em>"],
        "fields" : {f:{} for f in fields}
        }
    
    

    
    res = es.search(index=index_name, query=final_query, highlight=highlight)
    result_count =  res["hits"]["total"]["value"]
    _ids = [r["_id"] for r in res["hits"]["hits"]]
    # print(_ids)
    highlight = [r["highlight"] for r in res["hits"]["hits"] ]
    hits = [r["_source"] for r in res["hits"]["hits"]]
    scores = [r["_score"]*10 for r in res["hits"]["hits"]]
    return {"dataset_ids": _ids, "scores": scores, "highlights":highlight, "count": result_count, "datasets":hits}
    # return {"datasets": [r for r in res["hits"]["hits"]],"count":len(res["hits"]["hits"])}
    

@router.get("/organizations/{lang}", response_description="Search Organization by name or acronym")
async def search_datasets(request: Request, lang="fr"):    
    final_q = {"query":{"bool": { "should": {"terms": "name.label_"+{lang}, "terms":"acronym.label_"+lang}}}}
    res = es.search(index="gd4h_datasets", query=final_q)
    return {"datasets": [r["_id"] for r in res["hits"]["hits"]],"count":len(res["hits"]["hits"])}

            
            


