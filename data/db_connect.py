from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, conint, HttpUrl, EmailStr, AnyUrl
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie
import asyncio, motor


class Lang(str, Enum):
    fr = "fr"
    en = "en"


class Role(str, Enum):
    admin = "Administrateur"
    program = "Programmer"
    editor = "Editeur"
    reviewer = "Reviewer"
    public = "Public"

class ContactType(str, Enum):
    email = "email"
    name = "name"
    form = "formulaire" 
    
class Role(Document):
    pass


class OrgBase(BaseModel):
    pass


class UserBase(BaseModel):
    pass


class Reference(BaseModel):
    name_fr: str
    name_en: str
    uri: Optional[HttpUrl] = None


class AgentType(BaseModel):
    name_fr: str
    name_en: str
    uri: Optional[HttpUrl] = None


class OrganizationType(BaseModel):
    name_fr: str
    name_en: str
    uri: Optional[HttpUrl]


class Organization(OrgBase):
    name: str
    acronym: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    url: HttpUrl
    description: Optional[str] = None
    agent_type: AgentType
    organization_type: OrganizationType
    members: List[User] = []

class Dataset(Document):
    name:str
    description:str
    acronym: Optional[str]= None,
	organizations : List[Organization]
    url: AnyUrl
    contact: List[str]
    contact_type : [
	"url" : "https://www.data.gouv.fr/fr/datasets/reseau-permanent-de-mesure-de-bruit-de-la-metropole-de-lyon/#_",
	"contact" : [
		"Acoucité"
	],
	"contact_type" : [
		{
			"label_fr" : "email",
			"label_en" : "email"
		}
	],
	"contact_comments" : [
		{
			"label_fr" : "Acoucité",
			"label_en" : "Acoucity",
			"date" : ISODate("2022-01-17T22:00:47.827Z"),
			"user" : "admin"
		}
	],
	"data_domain" : {
		"label_fr" : "Environnement",
		"label_en" : null
	},
	"theme_category" : {
		"label_fr" : "Environnement",
		"label_en" : null
	},
	"thematic_field" : {
		"label_fr" : "Agents Physiques",
		"label_en" : null
	},
	"nature" : {
		"label_fr" : "Agents Physiques",
		"label_en" : null
	},
	"environment" : [
		{
			"label_fr" : "",
			"label_en" : ""
		}
	],
	"subthematic" : [
		{
			"label_fr" : "Mesures de bruit",
			"label_en" : "Noise measures"
		}
	],
	"exposure_factor_category" : [
		{
			"label_fr" : "Bruit",
			"label_en" : "Bruit"
		}
	],
	"exposure_factor" : [
		{
			"label_fr" : "Bruit",
			"label_en" : "Bruit"
		}
	],
	"has_filter" : true,
	"has_search_engine" : true,
	"has_missing_data" : false,
	"has_documentation" : true,
	"documentation_comments" : [
		{
			"label_fr" : "Notice d'utilisation de l'API",
			"label_en" : "API usage notice",
			"date" : ISODate("2022-01-17T22:00:48.094Z"),
			"user" : "admin"
		}
	],
	"is_downloadable" : true,
	"broadcast_mode" : [
		{
			"label_fr" : "Portail",
			"label_en" : null
		},
		{
			"label_fr" : "API",
			"label_en" : null
		}
	],
	"files_format" : [
		"Pdf",
		"Html",
		"Esri Shape",
		"Geojson"
	],
	"tech_comments" : [ ],
	"license_name" : {
		"label_fr" : "Licence Ouverte Etalab",
		"label_en" : null
	},
	"license_type" : [
		{
			"label_fr" : "Attribution",
			"label_en" : "Attribution"
		}
	],
	"has_pricing" : false,
	"legal_comments" : [ ],
	"has_restriction" : false,
	"has_compliance" : false,
	"is_geospatial_data" : true,
	"administrative_territory_coverage" : [
		"Lyon"
	],
	"geospatial_geographical_coverage" : [
		"LYON"
	],
	"geographical_information_level" : [
		{
			"label_fr" : "Site",
			"label_en" : "Site"
		}
	],
	"projection_system" : [
		"WGS84",
		"RGF93",
		"Lambert93"
	],
	"related_geographical_information" : false,
	"geo_comments" : [
		{
			"label_fr" : "false",
			"label_en" : "false",
			"date" : ISODate("2022-01-17T22:00:48.219Z"),
			"user" : "c24b"
		}
	],
	"year" : [
		"2006",
		"en cours"
	],
	"temporal_scale" : [
		"Non renseigné"
	],
	"update_frequency" : {
		"label_fr" : "Hebdomadaire",
		"label_en" : "Hebdomadaire"
	},
	"automatic_update" : null,
	"last_updated" : "2020-01-06T00:03:00.000Z",
	"last_inserted" : "2021-01-21T00:04:00.000Z",
	"last_modification" : "2021-01-21T00:04:00.000Z",
	"related_referentials" : [
		""
	],
	"other_access_points" : [
		"https://www.grandlyon.com/services/cartes-du-bruit.html"
	],
	"context_comments" : [ ],
	"comments" : [
		{
			"label_fr" : "",
			"label_en" : "",
			"date" : ISODate("2022-01-17T22:00:48.345Z"),
			"user" : "admin"
		}
	]
}

class User(UserBase):
    email: EmailStr
    first_name: str = None
    last_name: str = None
    organization: Organization
    roles: Role = Role.public
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    lang: Lang = Lang.fr


Dataset.update_forward_refs()
Organization.update_forward_refs()
User.update_forward_refs()

if __name__ == "__main__":
    a = AgentType(**{"name_fr": "AG", "name_en": "GA", "uri": "http://uri.com/#"})
    print(a.name_fr)
