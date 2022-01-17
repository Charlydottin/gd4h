#!/usr/bin/env python3
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from config import settings
from fastapi import FastAPI
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware

from apps.organization.routers import router as org_router
from apps.dataset.routers import router as dataset_router
from apps.references.routers import router as ref_router
from apps.comments.routers import router as comment_router
# from apps.search.routers import router as search_router
# from apps.translate.routers import router as translate_router
# from apps.filter.routers import router as translate_router


from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import RedirectResponse

from fastapi import APIRouter, Body, Request, HTTPException, status
import os

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
app.pymongodb_client = MongoClient(settings.DB_URL)


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(org_router, tags=["organizations"], prefix="/organizations")
app.include_router(dataset_router, tags=["datasets"], prefix="/datasets")
app.include_router(ref_router, tags=["references"], prefix="/references")
app.include_router(comment_router, tags=["comments"], prefix="/comments")
# app.include_router(translate_router, tags=["translations"], prefix="/translate")
# app.include_router(search_router, tags=["search"], prefix="/search")
# app.include_router(filter_router, tags=["filter"], prefix="/filter")



@app.get("/")
async def root():
    response = RedirectResponse(url='/docs')
    return response


# if __name__ == "__main__":
#     print(settings.HOST, settings.PORT)
#     uvicorn.run(
#         "main:app",
#         host=settings.HOST,
#         reload=settings.DEBUG_MODE,
#         port=settings.PORT
#     )
