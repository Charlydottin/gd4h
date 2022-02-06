#!/usr/bin/.env/python3.9
# file: routers.py

# from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

# from .models import Reference

# router = CRUDRouter(schema=Reference)

from .models import Reference
import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status,Query, Form
from fastapi.responses import JSONResponse


from bson import json_util

router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/", response_description="Get all references")
async def get_references(request: Request):
    references = []
    for doc in await request.app.mongodb["references"].find({}).to_list(length=50):
        references.append(doc)
    if len(references) == 0:
        raise HTTPException(status_code=404, detail=f"No reference found")
    return parse_json(references)

@router.get("/{item_id}", response_description="Get one reference")
async def get_reference(request: Request, item_id: str):
    if (reference := await request.app.mongodb["references"].find_one({"_id": ObjectId(item_id)})) is not None:
        return parse_json(reference)
    raise HTTPException(status_code=404, detail=f"reference {item_id} not found")

@router.get("/{reference_name}/details", response_description="Get values for one reference")
async def get_reference_values(request: Request, reference_name: str):
    references_values = []
    for doc in await request.app.mongodb[f"ref_{reference_name}"].find({}, {}).to_list(length=50):
        references_values.append(doc)
    if len(references_values) == 0:
        raise HTTPException(status_code=404, detail=f"No reference for {reference_name} found")
    return parse_json(references_values)

@router.post("/", response_description="Add an reference")
async def create_reference(request:Request, reference: Reference = Body(...), lang:str="fr"):   
    reference = parse_json(reference)
    # org = {"en":{}, "fr":{}}
    # org[lang] = reference
    # #here translate
    # #other_lang = SWITCH_LANGS(lang)
    # #org[other_lang] = translate_doc(reference, _from=lang)
    new_reference = await request.app.mongodb["references"].insert_one(reference)
    created_reference = await request.app.mongodb["references"].find_one({"_id": new_reference.inserted_id})
    # index_document(reference, created_org)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_reference)


@router.delete("/{item_id}", response_description="Delete a reference")
async def delete_reference(request: Request, item_id: str):   
    new_reference = await request.app.mongodb["references"].delete_one({"_id": ObjectId(item_id)})
    created_reference = await request.app.mongodb["references"].find_one({"_id": new_reference.inserted_id})
    # index_document(reference, created_org)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_reference)
