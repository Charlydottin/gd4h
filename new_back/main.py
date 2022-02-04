#!/usr/bin/env python3.9

from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
# import beanie
# from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from apps.comment.routers import router as comment_router
# from apps.comment.models import Comment

from apps.dataset.routers import router as dataset_router
# from apps.dataset.models import Dataset

from apps.organization.routers import router as organization_router
# from apps.organization.models import Organization

# from apps.reference.routers import router as reference_router
# from apps.reference.models import Reference


app = FastAPI()

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client["GD4H_V2"]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# @app.on_event("startup")
# async def app_init():
#     """Initialize application services"""
#     app.db = AsyncIOMotorClient("mongodb://localhost:27017").account
#     await init_beanie(app.db, document_models=[UserModel, DatasetModel])

app.include_router(comment_router, tags=["comments"], prefix="/comments")
app.include_router(dataset_router, tags=["datasets"], prefix="/datasets")
app.include_router(organization_router, tags=["organizations"], prefix="/organizations")
# app.include_router(reference_router, tags=["references"], prefix="/references")
@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response