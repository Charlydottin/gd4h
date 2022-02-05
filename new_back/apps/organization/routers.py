#!/usr/bin/.env/python3.9
# file: routers.py

from fnmatch import translate
import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status,Query
from fastapi.responses import JSONResponse

from typing import Optional


from bson import json_util
from .models import (Organization, OrganizationEn, FilterOrganizationFr, FilterOrganizationEn)
from .services import search_documents, index_document, get_indexed_fieldnames 
from .services import sync_get_filters

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
    index_document(organization, created_org)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_org)

@router.put("/{item_id}", response_description="Update a organization")
async def update_organization(request:Request, item_id: str, organization: Organization = Body(...), lang:str="fr"):
    organization = parse_json(organization)
    stored_organization = {"en":{}, "fr":{}}
    stored_organization[lang] = organization
    #here translate
    #other_lang = SWITCH_LANGS(lang)
    #org[other_lang] = translate_doc(organization, _from=lang)
    #here index
    # update_organization= {lang: organization}
    # new_organization = await request.app.mongodb["organizations"].update_one({"_id": ObjectId(item_id), {"$set":{lang:organization}})
    # created_organization = await request.app.mongodb["organizations"].find_one({"_id": new_organization.inserted_id})
    # #here index document at insert
    # index_document("organization", create_organization)
    # return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_organization)
    raise NotImplemented
    
@router.get("/search", response_description="Search for organizations using full_text_query")
async def search_organizations(request:Request, query: Optional[str] = Query(None, min_length=2, max_length=50), lang:str="fr"):
    #from rules get_indexed_fields()
    fields = get_indexed_fieldnames(model="organization")
    # fields = []
    # for doc in await request.app.mongodb["rules"].find({"model": "organization", "is_indexed": True},{"slug":1}).to_list(length=100):
    #     fields.append(doc["slug"])
    final_query = {
        "multi_match" : {
        "query":    query.strip(), 
        "fields": fields
        }
    }
    highlight = {
        
        "pre_tags" : "<em class='tag-fr highlight'>",
        "post_tags" :"</em>",
        "fields" : {f:{} for f in fields }
        }
    results = search_documents(final_query, highlight, model="organization", lang=lang)
    if len(results["count"]) == 0:
        raise HTTPException(status_code=404, detail=f"No organizations found for query={results['query']} not found")   
    return results

@router.get("/filters")
def get_filters(request:Request, lang: str="fr"):
    filters = sync_get_filters(lang)
    # filters = []
    # for facet in request.app.mongodb["rules"].find({"model": "organization", "is_facet": True}).to_list(length=5):
    #     filter_d = {
    #         "name": facet["slug"], 
    #         "is_controled":facet["is_controled"], 
    #         "is_multiple":facet["multiple"], 
    #         "is_bool": facet["datatype"] == "boolean",
    #         "values":[],
    #     }
    #     if facet["is_controled"]:
    #         filter_d["values"] = request.app.mongodb[facet["reference_table"]].distinct(f"name_{lang}")
    #     elif facet["datatype"] == "boolean":
    #         filter_d["values"] = [True, False]
    #     filters.append(filter_d)
    # if len(filters) == 0:
    #     raise HTTPException(status_code=404, detail=f"No Organization found")
    return parse_json(filters)

@router.post("/filter")
async def filter_organizations(request:Request, filter:FilterOrganizationFr, lang:str="fr"):
    req_filter = await request.json()
    index_name = f"organizations_{lang}"
    print(req_filter)
    if len(req_filter) == 1:
        param_k = list(req_filter.keys())[0]
        param_v = list(req_filter.values())[0]
        if param_k == "organizations":
            final_q = {"match": {param_k+".name": {"query": param_v}}}
        else:
            final_q = {"match": {param_k: {"query": param_v}}}
        # highlight = {}
        # results = search_documents(final_q, highlight,model="organization", lang=lang)
        
    else:
        must = []
        for key, val in req_filter.items():
            if key == "organizations":
                must.append({"match":{key+"name":val}})
            else:
                must.append({"match":{key:val}})
        final_q = {"bool" : { "must":must}}
    highlight = {}
    results = search_documents(final_q, highlight, model="organization", lang=lang)
    if results["count"] == 0:
        raise HTTPException(status_code=404, detail=f"No organizations found for query={results['query']} not found")        
    return results


@router.get("/{item_id}", response_description="Get one organization")
async def get_organization(request: Request, item_id: str, lang:str = "fr"):
    if (organization := await request.app.mongodb["organizations"].find_one({"_id": ObjectId(item_id)})) is not None:
        doc_id = organization["_id"]
        doc = organization[lang]
        doc["_id"] = str(doc_id)
        return parse_json(doc)
    raise HTTPException(status_code=404, detail=f"Organization {item_id} not found")
