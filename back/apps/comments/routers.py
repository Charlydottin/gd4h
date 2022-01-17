from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .models import CommentList, CommentModel
from bson import json_util, ObjectId 
import json

def parse_json(data):
    return json.loads(json_util.dumps(data))


router = APIRouter()

@router.get("/", response_description="List comments")
async def list_comments(request: Request):
    referentials = []
    for doc in await request.app.mongodb["comments"].find().to_list(length=100):
        doc["id"] = str(doc["_id"])
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"Comments not found")    



@router.post("/", response_description="Create a new comment")
async def create_reference(request: Request, referential: CommentModel = Body(...)):
    referential = jsonable_encoder(referential)
    new_referential = await request.app.mongodb["comments"].insert_one(referential)
    # collection_name = referential["scope"]+"s_metadata"
    # new_referential = await request.app.mongodb["references"].insert_one(referential)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_referential)

@router.delete("/{id}", response_description="Delete Comment")
async def delete_dataset(id: str, request: Request):
    delete_result = await request.app.mongodb["comments"].delete_one({"id": id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Comment {id} not found")
