from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator, root_validator 
from typing import Optional
# from config import settings
from enum import Enum
from pymongo import MongoClient

mongodb_client = MongoClient("mongodb://localhost:27017")
DB = mongodb_client.demo

def get_valid_agent_types():
    return DB.ref_agent_type.distinct("label_fr")

def get_valid_organization_types():
    return DB.ref_organization_type.distinct("label_fr")

def get_valid_image_mimetype():
    return ["png", "jpeg", "jpg", "gif", "svg"]

class OrganizationModel(BaseModel):
    id: Optional[str]
    name: str
    acronym: Optional[str]
    agent_type: str
    organization_type:str
    agent_type_fr:Optional[str]
    agent_type_en:Optional[str]
    agent_type_uri:Optional[HttpUrl]
    organization_type_fr:Optional[str]
    organization_type_en:Optional[str]
    organization_type_uri:Optional[HttpUrl]
    image_url: HttpUrl
    url: HttpUrl
    @validator("agent_type")
    def validate_agent_type(cls, agent_type: str):
        valid_agent_types =  get_valid_agent_types()
        if  agent_type not in valid_agent_types:
            raise ValueError("Agent Type is not valid")
        return agent_type
    @validator("organization_type")
    def validate_organization_type(cls, organization_type: str):
        valid_organization_types =  get_valid_organization_types()
        if  organization_type not in valid_organization_types:
            raise ValueError("Organization Type is not valid")
        # return organization_type

    @validator("image_url")
    def validate_image_url(cls, image_url: HttpUrl):
        valid_image_type = [image_url.endswith(n) for n in get_valid_image_mimetype()]
        if any(valid_image_type) is False:
            raise ValueError("Image Url is not valid")
            # return default_image_url
        return image_url

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "MSORG",
                "acronym": "My Super Org",
                "organization_type": "EPIC",
                "agent_type": "Entreprise",
                "image_url": "http://example.com/logo.png",
                "url": "http://my.super.org"
            }
        }
    @root_validator
    def _translate(cls, values):
        for translated_value in ["agent_type", "organization_type"]: 
            fr_value = values.get(translated_value)
            if fr_value is not None:
                values[translated_value+"_fr"] = fr_value
                en_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
                if en_value is not None:
                    values[translated_value+"_en"] = en_value.get("label_en")
            uri_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
            if uri_value is not None:
                values[translated_value+"_uri"] = uri_value.get("uri")
        return values
    @root_validator
    def _cast_id(cls, values):
        bson_id = values.get("_id")
        if bson_id is not None:
            values["id"] = str(bson_id)
        return values

class EditOrganizationModel(BaseModel):
    agent_type: Optional[str]
    organization_type: Optional[str]
    acronym: Optional[str]
    image_url:Optional[HttpUrl]
    url:Optional[HttpUrl]
    name:Optional[str]

    @validator("agent_type")
    def validate_agent_type(cls, agent_type: str):
        valid_agent_types =  get_valid_agent_types()
        if  agent_type not in valid_agent_types:
            raise ValueError("Agent Type is not valid")
        return agent_type
    @validator("organization_type")
    def validate_organization_type(cls, organization_type: str):
        valid_organization_types =  get_valid_organization_types()
        if  organization_type not in valid_organization_types:
            raise ValueError("Organization Type is not valid")
        return organization_type
    @root_validator(pre=False)
    def _translate(cls, values):
        for translated_value in ["agent_type", "organization_type"]: 
            fr_value = values.get(translated_value)
            if fr_value is not None:
                values[translated_value+"_fr"] = fr_value
                en_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
                if en_value is not None:
                    values[translated_value+"_en"] = en_value.get("label_en")
            uri_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
            if uri_value is not None:
                values[translated_value+"_uri"] = uri_value.get("uri")
        return values
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "organization_type": "EPA"                
            }
        }

class UpdateOrganizationModel(BaseModel):
    name: str
    acronym: Optional[str]
    agent_type: str
    organization_type:str
    agent_type_fr:Optional[str]
    agent_type_en:Optional[str]
    agent_type_uri:Optional[HttpUrl]
    organization_type_fr:Optional[str]
    organization_type_en:Optional[str]
    organization_type_uri:Optional[HttpUrl]
    image_url: HttpUrl
    url: HttpUrl
    @validator("agent_type")
    def validate_agent_type(cls, agent_type: str):
        valid_agent_types =  get_valid_agent_types()
        if  agent_type not in valid_agent_types:
            raise ValueError("Agent Type is not valid")
        return agent_type
        
    @validator("organization_type")
    def validate_organization_type(cls, organization_type: str):
        valid_organization_types =  get_valid_organization_types()
        if  organization_type not in valid_organization_types:
            raise ValueError("Organization Type is not valid")
        return organization_type

    @validator("image_url")
    def validate_image_url(cls, image_url: HttpUrl):
        valid_image_type = [image_url.endswith(n) for n in get_valid_image_mimetype()]
        if any(valid_image_type) is False:
            raise ValueError("Image Url is not valid")
            # return default_image_url
        return image_url
    @root_validator(pre=False)
    def _translate(cls, values):
        for translated_value in ["agent_type", "organization_type"]: 
            fr_value = values.get(translated_value)
            if fr_value is not None:
                values[translated_value+"_fr"] = fr_value
                en_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
                if en_value is not None:
                    values[translated_value+"_en"] = en_value.get("label_en")
            uri_value = DB["ref_"+translated_value].find_one({translated_value+"_fr": fr_value})
            if uri_value is not None:
                values[translated_value+"_uri"] = uri_value.get("uri")
        return values

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "My super organization",
                "acronym": "MSORG",
                "organization_type": "EPIC",
                "agent_type": "Entreprise",
                "image_url": "http://example.com/logo.png",
                "url": "http://mysuper.org"
            }
        }