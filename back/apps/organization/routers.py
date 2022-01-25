import json 
from bson import json_util, ObjectId 
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from .models import OrganizationModel, UpdateOrganizationModel, EditOrganizationModel

def parse_json(data):
    return json.loads(json_util.dumps(data))




router = APIRouter()

# Organizations

@router.get("/", response_description="List all organizations")
async def list_organizations(request: Request):
    organizations = []
    for doc in await request.app.mongodb["organizations"].find({}, {"logs":0}).to_list(length=300):
        doc["id"] = str(doc["_id"])
        organizations.append(doc)
    return parse_json(organizations)

@router.get("/{id}", response_description="Get a single organization")
async def show_organizations(id: str, request: Request):
    if (organization := await request.app.mongodb["organizations"].find_one({"_id":ObjectId(id)}, { "logs":0})) is not None:
        return parse_json(organization)
    raise HTTPException(status_code=404, detail=f"Organization {id} not found")


@router.get("/{id}/datasets/", response_description="List datasets belonging to this organization")
async def show_datasets_organizations(id: str, request: Request):
    datasets = []
    for doc in await request.app.mongodb["datasets"].find({"organizations._id":ObjectId(id)}).to_list(length=300):
        doc["id"] = str(doc["_id"])
        datasets.append(doc)
    if len(datasets) == 0:
        raise HTTPException(status_code=404, detail=f"Organization {id} not found in datasets")
    else:
        return parse_json(datasets)
    
@router.get("/{name}", response_description="Search a single organization by its name")
async def search_organizations(name: str, request: Request):
    if (organization := await request.app.mongodb["organizations"].find_one({"name": {"$regex": name}}, {"logs":0})
    ) is not None:
        return {"id":organization["id"], "name": name}
    raise HTTPException(status_code=404, detail=f"Organization '{name}' not found")


@router.put("/{id}", response_description="Update an organization")
async def update_organization(id: str, request: Request, organization: UpdateOrganizationModel = Body(...)):
    organization = {k: v for k, v in organization.dict().items() if v is not None and v!=""}
    update_result = await request.app.mongodb["organizations"].update_one(
            {"id": id}, {"$set": organization}
        )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=parse_json(organization))


@router.patch("/{id}", response_description="Partially update an organization", status_code=202)
async def partial_update_organization(id: str, request: Request, organization: EditOrganizationModel = Body(...)):
    organization = {k: v for k, v in organization.dict().items() if v is not None}
    if len(organization) >= 1:
        update_result = await request.app.mongodb["organizations"].update_one(
            {"id": id}, {"$set": organization}
        )

        if update_result.modified_count == 1:
            if (
                updated_organization := await request.app.mongodb["organizations"].find_one({"id": id}, {"logs":0})
            ) is not None:
                return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=parse_json(updated_organization))
                # updated_organization

    if (
        existing_organization := await request.app.mongodb["organizations"].find_one({"id": id}, { "logs":0})
    ) is not None:
        return JSONResponse(status_code=status.HTTP_304_NOT_MODIFIED, content=parse_json(existing_organization))

    raise HTTPException(status_code=404, detail=f"Organization {id} not found")

@router.post("/", response_description="Add new organization", status_code=201)
async def create_organization(request: Request, organization: OrganizationModel = Body(...)):
    org = parse_json(organization)
    new_organization = await request.app.mongodb["organizations"].insert_one(org)
    
    u_organization = await request.app.mongodb["organizations"].update_one(
            {"_id": new_organization.inserted_id}, {"$set": {"id": str(new_organization.inserted_id)}}
        )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=parse_json(u_organization))


@router.delete("/{id}", response_description="Delete organization")
async def delete_organization(id: str, request: Request):
    delete_result = await request.app.mongodb["organizations"].delete_one({"id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f" Organization {id} not found")


# @router.get("/filter/{lang}/{key}/{value}/", response_description="Filter organization by value")
# async def search_datasets(request: Request, lang:str, key:str, value:str):    
#     doc = request.app.mongodb["meta_fields"].find_one({"slug": key})
#     if doc["translation"] is True:
#         search_key = { key+'.label_'+lang: value }
#     else:
#         search_key = { key: value }
#     datasets = []
#     for doc in await request.app.mongodb["datasets"].find(search_key, {"_id":0}).to_list(length=100):
#         datasets.append(doc)
#     return {"organizations": datasets}
