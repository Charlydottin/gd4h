#!/usr/bin/.env/python3.9
# file: routers.py

from .models import Comment
import json
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Request, HTTPException, status,Query
from fastapi.responses import JSONResponse


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

@router.post("/{lang}", response_description="Add an comment")
async def create_comment(request:Request, comment: Comment = Body(...), lang:str="fr"):   
    comment = parse_json(comment)
    # org = {"en":{}, "fr":{}}
    # org[lang] = comment
    # #here translate
    # #other_lang = SWITCH_LANGS(lang)
    # #org[other_lang] = translate_doc(comment, _from=lang)
    new_comment = await request.app.mongodb["comments"].insert_one(comment)
    created_comment = await request.app.mongodb["comments"].find_one({"_id": new_comment.inserted_id})
    # index_document(comment, created_org)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_comment)


@router.delete("/{item_id}", response_description="Delete a comment")
async def delete_comment(request: Request, item_id: str):   
    new_comment = await request.app.mongodb["comments"].delete_one({"_id": ObjectId(item_id)})
    created_comment = await request.app.mongodb["comments"].find_one({"_id": new_comment.inserted_id})
    # index_document(comment, created_org)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_comment)
