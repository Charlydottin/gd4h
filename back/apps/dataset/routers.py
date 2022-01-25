from fastapi import APIRouter, Body, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .models import DatasetModel, UpdateDatasetModel
from typing import Optional, List
import json
from bson import json_util, ObjectId
from elasticsearch7 import Elasticsearch

es = Elasticsearch("http://localhost:9200")
    
router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))


@router.get("/", response_description="List all datasets")
async def list_datasets(request: Request):
    organizations = []
    for doc in await request.app.mongodb["datasets"].find({}).to_list(length=200):
        organizations.append(doc)
    if len(organizations) == 0:
        raise HTTPException(status_code=404, detail=f"No Datasets found")
    return parse_json(organizations)

@router.get("/count", response_description="Count datasets")
async def list_datasets(request: Request):
    datasets = await request.app.mongodb["datasets"].count_documents({})
    return datasets

@router.post("/", response_description="Add new dataset")
async def create_dataset(request: Request, dataset: DatasetModel = Body(...)):
    dataset = jsonable_encoder(dataset)
    new_dataset = await request.app.mongodb["datasets"].insert_one(dataset)
    created_dataset = await request.app.mongodb["datasets"].find_one(
        {"_id": new_dataset.inserted_id}
    )
    u_dataset = await request.app.mongodb["datasets"].update_one({"_id":new_dataset.inserted_id}, {"$set": {"id": str(new_dataset.inserted_id)}})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=parse_json(u_dataset))


@router.get("/{id}", response_description="Get a single dataset")
async def show_dataset(id: str, request: Request):
    if (dataset := await request.app.mongodb["datasets"].find_one({"_id": ObjectId(id)})) is not None:
        return parse_json(dataset)
    raise HTTPException(status_code=404, detail=f"Dataset {id} not found")


@router.get("/filter/{lang}", response_description='Filter datasets using parameters')
async def filter_datasets(lang:str, request: Request):
    index_name = f"datasets_{lang}"
    references = []
    for doc in await request.app.mongodb["meta_fields"].find({"model": "Dataset", "order":{"$ne":"-1"}, 
            "is_facet": True, "$or":[{"is_controled":True}, {"datatype":"bool"}]},{"slug":1}
        ).to_list(length=100):
        references.append(doc["slug"])
    params = request.query_params._dict
    print(params)
    if len(params) == 1:
        param_k = list(params.keys())[0]
        param_v = list(params.values())[0]
        if param_k == "organizations":
            final_q = {"match": {param_k+".name": {"query": param_v}}}
        elif param_k in references:
            final_q = {"match": {param_k: {"query": param_v}}}
            print(final_q)
            res = es.search(index=index_name, query=final_q)
            print(res)
            result_count =  res["hits"]["total"]["value"]
            results = []
            if result_count > 0:
            
                for r in res["hits"]["hits"]:
                    result = r["_source"]
                    result["_id"] = r["_id"]
                    result["score"] = str(round(r["_score"]*10,2))+"%"
                    results.append(result)
            return {"results":results, "count": result_count}
        else: 
            print("Error", param_k, "not a facet")
    else:
        must = []
        for key, val in params.items():
            if key == "organizations":
                must.append({"match":{key+"name":val}})
            elif key not in references:
                    print("Error", key, "not a facet")
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
        print(">>>", final_query)
        res = es.search(index=index_name, query=final_query)
        print("res", res)
        result_count =  res["hits"]["total"]["value"]
        results = []
        if result_count > 0:
        
            for r in res["hits"]["hits"]:
                result = r["_source"]
                result["_id"] = r["_id"]
                result["score"] = str(round(r["_score"]*10,2))+"%"
                # result["highlight"] = r["highlight"]
                results.append(result)
        return {"results":results, "count": result_count}
    

@router.get("/search/{lang}", response_description='Search dataset using full text')
async def search_datasets(lang:str, q: Optional[str] = Query(None, min_length=2, max_length=50)):
    fields = ['name', 'acronym', 'description', 'environment', 'nature', 'subthematic', 'exposure_factor', 'exposure_factor_category', 'theme_category', "organization"]
    index_name = f"datasets_{lang}"
    tokens = q.strip().split()
    
    final_query = {
        "multi_match" : {
        "query":    q, 
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
        result["highlight"] = r["highlight"]
        results.append(result)
    return {"results":results, "count": result_count}


@router.get("/references/{filter}/values/{lang}", response_description="Get all possible values for one controled field in a given lang")
async def get_filter_values(filter:str, lang:str, request: Request):
    rule = request.app.mongodb["meta_fields"].find_one({"model":"Dataset", "slug": filter, "is_controled": True})
    refs = []
    if rule["reference_table"] != "":
        for rf in await request.app.mongodb[rule["reference_table"]].distinct("label_"+lang):
            refs.append(rf)
    return {"values": refs}



@router.put("/{id}", response_description="Update a dataset")
async def update_dataset(id: str, request: Request, dataset: UpdateDatasetModel = Body(...)):
    dataset = {k: v for k, v in dataset.dict().items() if v is not None}
    if len(dataset) >= 1:
        update_result = await request.app.mongodb["datasets"].update_one(
            {"id": id}, {"$set": dataset}
        )

        if update_result.modified_count == 1:
            if (
                updated_dataset := await request.app.mongodb["datasets"].find_one({"id": id}, {"_id": 0})
            ) is not None:
                return parse_json(updated_dataset)

    if (
        existing_dataset := await request.app.mongodb["datasets"].find_one({"id": id}, {"_id":0})
    ) is not None:
        return parse_json(existing_dataset)

    raise HTTPException(status_code=404, detail=f"Dataset {id} not found")


@router.delete("/{id}", response_description="Delete Dataset")
async def delete_dataset(id: str, request: Request):
    
    delete_result = await request.app.mongodb["datasets"].delete_one({"id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Dataset {id} not found")
