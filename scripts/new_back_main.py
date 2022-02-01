#!/usr/bin/env python3.9


from fastapi import FastAPI
# import beanie
# from beanie import init_beanie
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient

from apps.log.routers import router as log_router
from apps.log.models import LogModel
from apps.organization.routers import router as org_router
from apps.organization.models import OrganizationModel
from apps.dataset.routers import router as dataset_router
from apps.dataset.models import DatasetModel
from apps.rules.routers import router as rule_router
from apps.rules.models import RulesModel
from apps.reference.routers import router as ref_router
from apps.reference.models import ReferenceModel
from apps.comment.routers import router as comment_router
from apps.comment.models import CommentModel
from apps.user.routers import router as user_route
from apps.user.models import  UserModel
from apps.role.routers import router as role_route
from apps.role.models import  RoleModel
# from apps.search.routers import router as search_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

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

# @app.on_event("startup")
# async def startup_db_client():
#     app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
#     app.mongodb = app.mongodb_client["GD4H_V2"]
    
# @app.on_event("shutdown")
# async def shutdown_db_client():
#     app.mongodb_client.close()

# @app.on_event("startup")
# async def app_init():
#     """Initialize application services"""
#     app.db = AsyncIOMotorClient("mongodb://localhost:27017").account
#     await init_beanie(app.db, document_models=[UserModel, DatasetModel])


app.include_router(org_router, tags=["organizations"], prefix="/organizations")
app.include_router(dataset_router, tags=["datasets"], prefix="/datasets")
app.include_router(ref_router, tags=["references"], prefix="/references")
app.include_router(comment_router, tags=["comments"], prefix="/comments")



@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response