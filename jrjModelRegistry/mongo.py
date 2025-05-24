from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId  # <-- YOU FORGOT THIS
from bson.errors import InvalidId
import json
import datetime

from datetime import datetime, UTC

import os
from . import jrjModelRegistryConfig

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

jrjModelRegistryDb = ''
mongoConfigDict = {
    "jrjModelRegistryDbColModels" : None
}


def initMongodb():
    clientMongoDb = MongoClient(jrjModelRegistryConfig.get('mongoConnection'), server_api=ServerApi('1'))
    try:
        clientMongoDb.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    jrjModelRegistryDb = clientMongoDb["jrjModelRegistry"]
    mongoConfigDict['jrjModelRegistryDbColModels'] = jrjModelRegistryDb["models"]
    mongoConfigDict['jrjModelRegistryDbColModels'].create_index([("modelName", 1)], background=True)
    mongoConfigDict['jrjModelRegistryDbColModels'].create_index(
        [("modelName", 1), ("version", 1)],
        unique=True,
        background=True
    )

if jrjModelRegistryConfig.get('mongoConnection') != 'JRJ_MONGODB_MODEL_REGISTRY':
    initMongodb()


def find_model_by_id(id: str):
    result = mongoConfigDict['jrjModelRegistryDbColModels'].find_one({"_id": ObjectId(id)})
    return json.loads(JSONEncoder().encode(result))

def find_model_by_idAndLoadModel(id: str):
    return find_model_by_id(id)

def new_model(dataPayload: dict):
    now = datetime.now(UTC)
    iso_string = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    dataPayload = {
        **dataPayload,
        "createdAt": iso_string,
        "updatedAt": iso_string
    }
    result = mongoConfigDict['jrjModelRegistryDbColModels'].insert_one(dataPayload)
    return find_model_by_id(f"{result.inserted_id}")



def search_models(input: dict, type: str = "findMany"):
    search_query = {}

    if input.get('where'):
        search_query.update(input['where'])

    if type == "findMany":
        # --- Optional Projection ---
        projection = input.get('select')  # Can be None, or a dict of included/excluded fields
        cursor = mongoConfigDict['jrjModelRegistryDbColModels'].find(search_query, projection)

        # --- Sort ---
        order_by = input.get('orderBy') or []
        if order_by:
            sort_fields = []
            for order in order_by:
                if not order:
                    continue
                for field_name, direction in order.items():
                    sort_fields.append(
                        (field_name, ASCENDING if str(direction).lower() == 'asc' else DESCENDING)
                    )
            if sort_fields:
                cursor = cursor.sort(sort_fields)

        # --- Pagination ---
        pagination = input.get('pagination') or {}
        page = max(pagination.get('page', 1), 1)
        size = max(pagination.get('size', 10), 1)
        cursor = cursor.skip(size * (page - 1)).limit(size)

        return list(cursor)

    elif type == "count":
        return mongoConfigDict['jrjModelRegistryDbColModels'].count_documents(search_query)


def search_models_common(body: dict):
    if body.get("type"):
        return search_models(body.get("search", {}), body["type"])
    data = search_models(body.get("search", {}), "findMany")
    count = search_models(body.get("search", {}), "count")
    return {"data": data, "count": count}


def update_model(id: str, update_obj: dict):
    now = datetime.now(UTC)
    iso_string = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    update_obj['updatedAt'] = iso_string
    result = mongoConfigDict['jrjModelRegistryDbColModels'].update_one(
        {"_id": ObjectId(id)},
        {"$set": update_obj}
    )
    return result.modified_count > 0

def delete_model(id: str):
    result = mongoConfigDict['jrjModelRegistryDbColModels'].delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0