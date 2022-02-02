#!/usr/bin/env python3.9


from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
# import beanie
# from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
{% for route, models in route_models%}
from apps.{{route}}.routers import router as {{route}}_router
from apps.{{route}}.models import {{models}}
{%endfor%}
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
{% for route,model in route_models%}
app.include_router({{route}}_router, tags=["{{route}}s"], prefix="/{{route}}s")
{% endfor %}



@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response