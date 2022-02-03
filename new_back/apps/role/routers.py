#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

from .models import RoleFr

fr_router = CRUDRouter(schema=RoleFr)


from .models import RoleEn

en_router = CRUDRouter(schema=RoleEn)

