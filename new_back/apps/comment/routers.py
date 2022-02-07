#!/usr/bin/.env/python3.9
# file: routers.py

from .models import Comment
import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status,Query
from fastapi.responses import JSONResponse
from datetime import datetime

from bson import json_util

router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/", response_description="Get all comments")
async def get_comments(request: Request):
    comments = []
    for doc in await request.app.mongodb["comments"].find({}).to_list(length=200):
        comments.append(doc)
    if len(comments) == 0:
        raise HTTPException(status_code=404, detail=f"No comment found")
    return parse_json(comments)

@router.get("/{item_id}", response_description="Get one comment")
async def get_comment(request: Request, item_id: str):
    if (comment := await request.app.mongodb["comments"].find_one({"_id": ObjectId(item_id)})) is not None:
        return parse_json(comment)
    raise HTTPException(status_code=404, detail=f"comment {item_id} not found")

@router.post("/", response_description="Add an comment")
async def create_comment(request:Request, comment: Comment = Body(...), lang:str="fr"):   
    dict_comment = comment.__dict__
    if dict_comment["ref_id"] is not None:
        new_comment =  {k:v for k,v in dict_comment.items() if k in ["user", "lang", "text", "date"]}
        #register comment into ref_id datasets
        if 'scope' in dict_comment and  (dict_comment['scope'] != '' or dict_comment['scope'] is not None):
            collection_name = f"{dict_comment['scope']}s"
            try:
                dataset_comment = await request.app.mongodb[collection_name].update_one(
                    {"_id": dict_comment["ref_id"]}, {"$push":{dict_comment["perimeter"]:new_comment}}
                )
            except Exception as e:
                print(e)
                raise HTTPException(status_code =422, detail=f"{e}.:\n. Scope \"{dict_comment['scope']}\" is incorrect: No {collection_name} in DB")
    #register comment in global dataset table
    new_comment = await request.app.mongodb["comments"].insert_one(comment.__dict__)
    created_comment = await request.app.mongodb["comments"].find_one({"_id": str(new_comment.inserted_id)})
    # # index_document(comment, created_org)
    # request.status_code = status.HTTP_201_CREATED
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_comment)
    
# @router.delete("/{item_id}", response_description="Delete a comment")
# async def delete_comment(request: Request, item_id: str):   
#     new_comment = await request.app.mongodb["comments"].delete_one({"_id": ObjectId(item_id)})
#     created_comment = await request.app.mongodb["comments"].find_one({"_id": new_comment.inserted_id})
#     # index_document(comment, created_org)
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_comment)
