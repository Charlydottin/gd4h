from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel


class Query(BaseModel):
    query: str
    class Config:
        schema_extra = {
            "example": "nvdi AND polluant"
            }

    