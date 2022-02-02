#!/usr/bin/env python3.9


from fastapi import FastAPI
from apps.organization.routers import router as org_router
from apps.dataset.routers import router as dataset_router
from apps.references.routers import router as ref_router
from apps.comments.routers import router as comment_router
from apps.search.routers import router as search_router
from fastapi.middleware.cors import CORSMiddleware

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