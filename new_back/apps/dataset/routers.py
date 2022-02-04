#!/usr/bin/.env/python3.9
# file: routers.py

import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status,Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from bson import json_util, ObjectId
from elasticsearch7 import Elasticsearch
from .models import Dataset
from .models import FilterDatasetFr
from typing import Optional

es = Elasticsearch("http://localhost:9200")
    
router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/", response_description="Get all datasets")
async def get_datasets(request: Request, lang:str = "fr"):
    datasets = []
    for doc in await request.app.mongodb["datasets"].find({}).to_list(length=120):
        doc_id = doc["_id"]
        doc = doc[lang]
        doc["_id"] = str(doc_id)
        datasets.append(doc)
    if len(datasets) == 0:
        raise HTTPException(status_code=404, detail=f"No Datasets found")
    return parse_json(datasets)

@router.get("/{item_id}", response_description="Get one dataset")
async def get_dataset(request: Request, item_id: str, lang:str = "fr"):
    if (dataset := await request.app.mongodb["datasets"].find_one({"_id": ObjectId(item_id)})) is not None:
        doc_id = dataset["_id"]
        doc = dataset[lang]
        doc["_id"] = str(doc_id)
        return parse_json(doc)
        # return jsonable_encoder(doc)
    raise HTTPException(status_code=404, detail=f"Dataset {item_id} not found")

@router.post("/", response_description="Add a dataset")
async def create_dataset(request:Request, dataset: Dataset = Body(...), lang:str="fr"):
    dataset = parse_json(dataset)
    stored_dataset = {"en":{}, "fr":{}}
    stored_dataset[lang] = dataset
    #here translate
    #other_lang = SWITCH_LANGS(lang)
    #org[other_lang] = translate_doc(organization, _from=lang)
    #here index
    new_dataset = await request.app.mongodb["datasets"].insert_one(stored_dataset)
    created_dataset = await request.app.mongodb["datasets"].find_one({"_id": new_dataset.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_dataset)

@router.get("/search", response_description="Search for datasets using full_text_query")
async def search_datasets(request:Request, query: Optional[str] = Query(None, min_length=2, max_length=50), lang:str="fr"):
    #from rules get_indexed_fields()
    fields = []
    for doc in await request.app.mongodb["rules"].find({"model": "dataset", "is_indexed": True},{"slug":1}).to_list(length=100):
        fields.append(doc["slug"])
    # fields = [
    #     'name', 
    #     'acronym', 
    #     'description', 
    #     'environment', 
    #     'nature', 
    #     'subthematic', 
    #     'exposure_factor', 
    #     'exposure_factor_category', 
    #     'theme_category',
    #     "organizations"
    # ]
    index_name = f"datasets_{lang}"
    tokens = query.strip()
    
    final_query = {
        "multi_match" : {
        "query":    tokens, 
        "fields": fields
        }
    }
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
        # result["highlight"] = r["highlight"]
        results.append(result)
    if len(results) >0:
        return {"results":results, "count": result_count, "query": query}
    raise HTTPException(status_code=404, detail=f"No datasets found for query={tokens} not found")   

# @router.post("/filter/", response_description="Search for datasets using filters")
# async def filter_datasets(request:Request, filter: Filter = Body(...), lang:str="fr"):
#     #from rules get_faceted_fields()
@router.get("/filters")
async def get_filters(request:Request, lang: str="fr"):
    filters = []
    for facet in await request.app.mongodb["rules"].find({"model": "dataset", "is_facet": True},{"slug":1}).to_list(length=100):
        field_name = facet["slug"]
        is_controled, is_multiple, is_bool = facet["is_controled"], facet["multiple"], facet["datatype"] == "boolean"
        filter_d = {
            "name": field_name, 
            "is_controled":is_controled, 
            "is_multiple":is_multiple, 
            "is_bool": is_bool,
            "values":[],
        }
        if is_controled:
            filter_d["values"] = request.app.mongodb[facet["reference_table"]].distinct(f"name_{lang}")
        elif is_bool:
            filter_d["values"] = [True, False]
        filters.append(filter_d)
    return {"filters":filters}

@router.post("/filter")
async def filter_datasets(request:Request, filter:FilterDatasetFr, lang:str="fr"):
    req_filter = await request.json()
    index_name = f"datasets_{lang}"
    print(req_filter)
    if len(req_filter) == 1:
        param_k = list(req_filter.keys())[0]
        param_v = list(req_filter.values())[0]
        if param_k == "organizations":
            final_q = {"match": {param_k+".name": {"query": param_v}}}
        else:
            final_q = {"match": {param_k: {"query": param_v}}}
        res = es.search(index=index_name, query=final_q)
        result_count =  res["hits"]["total"]["value"]
        results = []
        if result_count == 0:
            raise HTTPException(status_code=404, detail=f"No datasets found for query={req_filter} not found")   
        else:
            for r in res["hits"]["hits"]:
                result = r["_source"]
                result["_id"] = r["_id"]
                result["score"] = str(round(r["_score"]*10,2))+"%"
                results.append(result)
        return {"results":results, "count": result_count, "query":req_filter}
    else:
        must = []
        for key, val in req_filter.items():
            if key == "organizations":
                must.append({"match":{key+"name":val}})
            else:
                datatype = await request.app.mongodb["meta_fields"].find_one({"model": "Dataset", "slug":key})
                if datatype is not None:
                    if datatype["datatype"] == "str":
                        must.append({"match":{key:val}})
                    elif datatype["datatype"] == "bool":
                        must.append({"match":{key:bool(val)}})
                    else:
                        print("Error", key, "not searchable type")
                else:
                    print("Error", key, "no datatype")
        final_query = {"bool" : { "must":must}}
        res = es.search(index=index_name, query=final_query)
        result_count =  res["hits"]["total"]["value"]
        results = []
        if result_count == 0:
            raise HTTPException(status_code=404, detail=f"No datasets found for query={req_filter} not found")
        if result_count > 0:
            for r in res["hits"]["hits"]:
                result = r["_source"]
                result["_id"] = r["_id"]
                result["score"] = str(round(r["_score"]*10,2))+"%"
                # result["highlight"] = r["highlight"]
                results.append(result)
        return {"results":results, "count": result_count, "query": req_filter}

@router.post("/search")
async def filter_search_dataset(request:Request,filter:FilterDatasetFr,query: str = Query(None, min_length=2, max_length=50),lang: str="fr"):
    search_results = await search_datasets(request, query, lang)
    # if search_results["count"] == 0:
    #     raise HTTPException(status_code=404, detail=f"No datasets found for query={query} not found")
    req_filter = await request.json()
    print(req_filter)