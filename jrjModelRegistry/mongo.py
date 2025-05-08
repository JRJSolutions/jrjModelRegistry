from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId  # <-- YOU FORGOT THIS
from bson.errors import InvalidId
import json
import datetime

import os

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


if 'JRJ_MONGODB_MODEL_REGISTRY' in os.environ:


    JRJ_MONGODB_MODEL_REGISTRY = os.environ['JRJ_MONGODB_MODEL_REGISTRY']



    clientMongoDb = MongoClient(JRJ_MONGODB_MODEL_REGISTRY, server_api=ServerApi('1'))

    try:
        clientMongoDb.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    jrjModelRegistryDb = clientMongoDb["jrjModelRegistry"]
    jrjModelRegistryDbColModels = jrjModelRegistryDb["models"]
    jrjModelRegistryDbColModels.create_index([("modelName", 1)], background=True)
    jrjModelRegistryDbColModels.create_index(
        [("modelName", 1), ("version", 1)],
        unique=True,
        background=True
    )


def find_model_by_id(id: str):
    result = jrjModelRegistryDbColModels.find_one({"_id": ObjectId(id)})
    return json.loads(JSONEncoder().encode(result))

def find_model_by_idAndLoadModel(id: str):
    return find_model_by_id(id)

def new_model(dataPayload: dict):
    now = datetime.datetime.utcnow()
    iso_string = now.isoformat() + "Z"
    dataPayload = {
        **dataPayload,
        "createdAt": iso_string,
        "updatedAt": iso_string
    }
    result = jrjModelRegistryDbColModels.insert_one(dataPayload)
    return find_model_by_id(f"{result.inserted_id}")


def search_models(input: dict, type: str = "findMany"):
    search_query = {}

    if input.get('where'):
        search_query.update(input['where'])

    if type == "findMany":
        cursor = jrjModelRegistryDbColModels.find(search_query)

        # --- Fix for your orderBy format ---
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
        return jrjModelRegistryDbColModels.count_documents(search_query)


def search_models_common(body: dict):
    if body.get("type"):
        return search_models(body.get("search", {}), body["type"])
    data = search_models(body.get("search", {}), "findMany")
    count = search_models(body.get("search", {}), "count")
    return {"data": data, "count": count}


def update_model(id: str, update_obj: dict):
    now = datetime.datetime.utcnow()
    iso_string = now.isoformat() + "Z"
    update_obj['updatedAt'] = iso_string
    result = jrjModelRegistryDbColModels.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_obj}
    )
    return result.modified_count > 0

def delete_model(id: str):
    result = jrjModelRegistryDbColModels.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0