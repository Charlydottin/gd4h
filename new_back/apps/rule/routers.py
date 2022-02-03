#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

from .models import Rule

router = CRUDRouter(schema=Rule)

