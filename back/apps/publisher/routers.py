from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .models import PublisherModel

router = APIRouter()

# OrganizationType
@router.get("/", response_description="List publisher")
async def list_publisher_type(request: Request):
    organization_types = []
    for doc in await request.app.mongodb["publisher_type"].find({},{"_id":0}).to_list(length=100):
        organization_types.append(doc)
    return organization_types


@router.get("/lang/{lang}", response_description="List publisher by lang")
async def list_publisher_type(lang: str, request: Request):
    organization_types = []
    for doc in await request.app.mongodb["publisher_type"].find({},{"_id":0, "slug":1, "label_{}".format(lang): 1}).to_list(length=100):
        organization_types.append(doc)
    return organization_types


@router.get("/uri/", response_description="List publisher ADMS uri")
async def list_publisher_type(request: Request):
    organization_types = []
    for doc in await request.app.mongodb["publisher_type"].find({},{"_id":0, "slug":1, "adms_url":1}).to_list(length=100):
        organization_types.append(doc)
    return organization_types
