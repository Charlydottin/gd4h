from pymongo import MongoClient
from bson import ObjectId, json_util
from ..config import settings

pymongodb = MongoClient(settings.DB_URL)
