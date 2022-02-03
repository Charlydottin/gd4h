#!/usr/bin/.env/python3.9
# file: routers.py

import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse

from bson import json_util, ObjectId
from elasticsearch7 import Elasticsearch
from .models import Dataset

es = Elasticsearch("http://localhost:9200")
    
router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/", response_description="Get all datasets")
async def get_datasets(request: Request, lang:str = "fr"):
    datasets = []
    for doc in await request.app.mongodb["datasets"].find({}).to_list(length=200):
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
    raise HTTPException(status_code=404, detail=f"Dataset {item_id} not found")

@router.post("/{lang}", response_description="Add a dataset")
async def create_dataset(request:Request, dataset: Dataset = Body(...), lang:str="fr"):
    dataset = parse_json(dataset)
    stored_dataset = {"en":{}, "fr":{}}
    stored_dataset[lang] = dataset
    #here translate
    #other_lang = SWITCH_LANGS(lang)
    #org[other_lang] = translate_doc(organization, _from=lang)
    new_dataset = await request.app.mongodb["datasets"].insert_one(stored_dataset)
    created_dataset = await request.app.mongodb["datasets"].find_one({"_id": new_dataset.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_dataset)
