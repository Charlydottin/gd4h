from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .models import DatasetModel, UpdateDatasetModel
import json
from bson import json_util

router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.post("/", response_description="Add new dataset")
async def create_dataset(request: Request, dataset: DatasetModel = Body(...)):
    dataset = jsonable_encoder(dataset)
    new_dataset = await request.app.mongodb["datasets"].insert_one(dataset)
    created_dataset = await request.app.mongodb["datasets"].find_one(
        {"_id": new_dataset.inserted_id}
    )
    u_dataset = await request.app.mongodb["datasets"].update_one({"_id":new_dataset.inserted_id}, {"$set": {"id": str(new_dataset.inserted_id)}})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=parse_json(u_dataset))


@router.get("/", response_description="List all datasets")
async def list_datasets(request: Request):
    organizations = []
    for doc in await request.app.mongodb["datasets"].find({}).to_list(length=100):
        organizations.append(doc)
    if len(organizations) == 0:
        raise HTTPException(status_code=404, detail=f"No Datasets found")
    return parse_json(organizations)

@router.get("/{id}", response_description="Get a single dataset")
async def show_dataset(id: str, request: Request):
    if (dataset := await request.app.mongodb["datasets"].find_one({"id": id}, {"_id": 0})) is not None:
        return parse_json(dataset)
    raise HTTPException(status_code=404, detail=f"Dataset {id} not found")

@router.get("/{name}", response_description="Search a single dataset by name")
async def search_dataset(name: str, request: Request):
    if (dataset := await request.app.mongodb["datasets"].find_one({"dataset_name": {"$regex": name}})
    ) is not None:
        return parse_json(dataset)
    raise HTTPException(status_code=404, detail=f"Dataset'{name}' not found")

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
