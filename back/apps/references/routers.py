from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .models import ReferenceList, ReferenceModel
from bson import json_util, ObjectId 
import json

def parse_json(data):
    return json.loads(json_util.dumps(data))


router = APIRouter()

@router.get("/", response_description="List available references")
async def list_referentials(request: Request):
    referentials = []
    for doc in await request.app.mongodb["references"].find({}, {"_id":0}).to_list(length=100):
        doc["id"] = str(doc["_id"])
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"References not found")    

@router.get("/{reference_name}", response_description="get all values for a given reference")
async def get_references_values(reference_name: str, request: Request):
    table_ref = "ref_"+reference_name
    referentials = []
    for doc in await request.app.mongodb[table_ref].find({}, {"uri":0, "_id":0}).to_list(length=100):
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"Reference {reference_name} not found")    

@router.get("/meta/{model_name}", response_description="Get fields rules and description given a model")
async def list_referentials(model_name: str, request: Request):
    referentials = []
    for doc in await request.app.mongodb["meta_fields"].find({"model": model_name.title()}).to_list(length=100):
        doc["id"] = str(doc["_id"])
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"Fields {model_name.lower()} for not found")    

@router.get("/filters/{model_name}", response_description="Get fields that are used as filters given model_name")
async def list_referentials(model_name: str, request: Request):
    referentials = []
    for doc in await request.app.mongodb["meta_fields"].find({"model": model_name.title(), "order":{"$ne":"-1"}, "is_facet": True},
        {"section":1, "slug":1, "order":1, "label_fr":1, "label_en": 1, "translation":1, "multiple":1, "datatype":1,"is_controled":1,"reference_table":1, '_id':0}).to_list(length=100):
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"Filters for {model_name.lower()} not found") 

@router.get("/filters/{model_name}/values/{field_name}")
async def get_distinct_values_from_field(model_name:str, field_name: str, lang:str, request: Request):
    values = []
    for doc in await request.app.mongodb[model_name+"s"].distinct(field_name):
        values.append(doc)
    if len(values) > 0:
        return parse_json(values)
    else:
        raise HTTPException(status_code=404, detail=f"Values of {field_name} for {model_name.lower()} not found") 

@router.get("/<name>", response_description="Get reference detail by name")
async def list_referentials(request: Request, name: str):
    referentials = []
    for doc in await request.app.mongodb[name].find({}, {"_id":0}).to_list(length=100):
        doc["id"] = str(doc["_id"])
        referentials.append(doc)
    if len(referentials) > 0:
        return parse_json(referentials)
    else:
        raise HTTPException(status_code=404, detail=f"Referential {name} not found")    


# @router.post("/", response_description="Register a new reference list")
# async def create_referential(request: Request, referential: ReferenceList = Body(...)):
#     referential = jsonable_encoder(referential)
#     new_referential = await request.app.mongodb["references"].insert_one(referential)
#     # collection_name = referential["scope"]+"s_metadata"
#     # new_referential = await request.app.mongodb["references"].insert_one(referential)
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_referential)
    
# @router.put("/<", response_description="Edit a new reference list")
# async def create_referential(request: Request, referential: ReferenceList = Body(...)):
#     referential = jsonable_encoder(referential)
#     new_referential = await request.app.mongodb["references"].update_one({referential)
#     # collection_name = referential["scope"]+"s_metadata"
#     # new_referential = await request.app.mongodb["references"].insert_one(referential)
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_referential)

@router.post("/", response_description="Create a new reference")
async def create_reference(request: Request, referential: ReferenceModel = Body(...)):
    referential = jsonable_encoder(referential)
    table_name = referential["table_name"]
    del referential["table_name"]    
    new_referential = await request.app.mongodb[table_name].insert_one(referential)
    # collection_name = referential["scope"]+"s_metadata"
    # new_referential = await request.app.mongodb["references"].insert_one(referential)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_referential)

# @router.get("/{name}", response_description="Search a single referential by collection name")
# async def search_referential(name: str, request: Request):
#     if (dataset := await request.app.mongodb["referentials"].find_one({"collection": {"$regex": name}})
#     ) is not None:
#         return dataset
#     raise HTTPException(status_code=404, detail=f"Referential '{name}' not found")

# @router.put("/{id}", response_description="Update a referential")
# async def update_dataset(id: str, request: Request, referential: ReferentialModel = Body(...)):
#     referential = {k: v for k, v in referential.dict().items() if v is not None}
#     if len(referential) >= 1:
#         update_result = await request.app.mongodb["referentials"].update_one(
#             {"id": id}, {"$set": referential}
#         )

#         if update_result.modified_count == 1:
#             if (
#                 updated_dataset := await request.app.mongodb["referentials"].find_one({"id": id}, {"_id": 0})
#             ) is not None:
#                 return updated_dataset

#     if (
#         existing_dataset := await request.app.mongodb["referentials"].find_one({"id": id}, {"_id":0})
#     ) is not None:
#         return existing_dataset

#     raise HTTPException(status_code=404, detail=f"Referential {id} not found")

# @router.delete("/{id}", response_description="Delete Referential")
# async def delete_dataset(id: str, request: Request):
#     delete_result = await request.app.mongodb["referentials"].delete_one({"id": id})
#     if delete_result.deleted_count == 1:
#         return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
#     raise HTTPException(status_code=404, detail=f"Referential {id} not found")
