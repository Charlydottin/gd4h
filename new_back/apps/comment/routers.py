#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

from .models import Comment

router = CRUDRouter(schema=Comment)

