from typing import Optional
import uuid
import os
from datetime import date, datetime, time, timedelta
from pydantic import BaseModel, Field
# from fastapi_utils.enums import StrEnum
from ..organization.models import OrganizationModel
from typing import List
from pymongo import MongoClient
from pydantic import BaseModel, create_model

# DATABASE_NAME = "GD4H_V1"
# mongodb_client = MongoClient("mongodb://localhost:27017")
# DB = mongodb_client[DATABASE_NAME]

# from script.db import DB as db

# class NatureTypeFR(StrEnum):
#     # db.datasets.distinct("nature_fr")
#     none = ""
#     agent_physique = "Agents Physiques"
#     biodiv = "Biodiversité"
#     indic = "Indicateurs géographiques et socio-démographiques"
#     pesticides = "Pesticides"

# class DatarefTypeFR(StrEnum):
#     jdd = "Jeu de données"
#     portail = "Portail"

# class ThemeCatFR(StrEnum):
#     agri = "Agriculture, pêche, sylviculture et alimentation"
#     env = "Environnement"
#     pop = "Population et société"
#     urb = "Régions et villes"
#     sante = "Santé"
#     trans = "Transports"
    
# class DataDomainFR(StrEnum):
#     env ="Environnement"
#     ref = "Référentiel"
#     sante = "Santé" 

# class DatasetModelInfoFR(BaseModel):
#     name_fr: str = Field(...)

class DatasetModel(BaseModel):
    name: str 
    acronym: str
    description: str
    link: str 
    state: bool
    has_filter: bool
    has_search_engine: bool
    integration_status:bool
    is_opensource:bool
    has_restrictions:bool
    downloadable:bool
    is_geospatial_data:bool
    projection_system:list
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
        "example": {
            }
        }


class UpdateDatasetModel(BaseModel):
    pass