#!/usr/bin/.env/python3.9
# file: routers.py

from fnmatch import translate
import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse

from bson import json_util, ObjectId
from elasticsearch7 import Elasticsearch
from .models import Organization

es = Elasticsearch("http://localhost:9200")
    
router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/", response_description="Get all organizations")
async def get_organizations(request: Request, lang:str = "fr"):
    organizations = []
    for doc in await request.app.mongodb["organizations"].find({}).to_list(length=200):
        doc_id = doc["_id"]
        doc = doc[lang]
        doc["_id"] = str(doc_id)
        organizations.append(doc)
    if len(organizations) == 0:
        raise HTTPException(status_code=404, detail=f"No Organization found")
    return parse_json(organizations)

@router.get("/{item_id}", response_description="Get one organization")
async def get_organization(request: Request, item_id: str, lang:str = "fr"):
    if (organization := await request.app.mongodb["organizations"].find_one({"_id": ObjectId(item_id)})) is not None:
        doc_id = organization["_id"]
        doc = organization[lang]
        doc["_id"] = str(doc_id)
        return parse_json(doc)
    raise HTTPException(status_code=404, detail=f"Organization {item_id} not found")

@router.post("/{lang}", response_description="Add an organization")
async def create_organization(request:Request, organization: Organization = Body(...), lang:str="fr"):   
    organization = parse_json(organization)
    org = {"en":{}, "fr":{}}
    org[lang] = organization
    #here translate
    #other_lang = SWITCH_LANGS(lang)
    #org[other_lang] = translate_doc(organization, _from=lang)
    new_org = await request.app.mongodb["organizations"].insert_one(org)
    created_org = await request.app.mongodb["organizations"].find_one({"_id": new_org.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_org)
