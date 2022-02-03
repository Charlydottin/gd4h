#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

from .models import UserFr

fr_router = CRUDRouter(schema=UserFr)


from .models import UserEn

en_router = CRUDRouter(schema=UserEn)

