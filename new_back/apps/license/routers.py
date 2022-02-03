#!/usr/bin/.env/python3.9
# file: routers.py

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter

from .models import LicenseFr

fr_router = CRUDRouter(schema=LicenseFr)


from .models import LicenseEn

en_router = CRUDRouter(schema=LicenseEn)

