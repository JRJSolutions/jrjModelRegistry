import datetime
from fastapi import APIRouter, HTTPException, Request
import json
from bson import ObjectId
from bson import ObjectId  # <-- YOU FORGOT THIS
from bson.errors import InvalidId
import json

from jrjModelRegistry.jrjModelRegistry import deleteAJrjModelAsset, loadAJrjModel

from .mongo import JSONEncoder, delete_model, find_model_by_id, find_model_by_idAndLoadModel, new_model, search_models, search_models_common, update_model



jrjRouterModelRegistry = APIRouter(
    prefix="/jrjModelRegistry",   # Automatically prefixes all routes
    tags=["JRJ Model Registry"]   # Optional, useful for OpenAPI docs
)





class JrjMlModelRegistry:


    def __init__(self, config):
        pass
    def test(self, x):
        return x


@jrjRouterModelRegistry.get("/")
async def getRoot():
    return {"message": "Welcome to JRJ Model Registry"}

@jrjRouterModelRegistry.post("/newModel")
async def new_model_endpoint(request: Request):
    body = await request.json()
    result = new_model(body)
    return json.loads(JSONEncoder().encode(result))


@jrjRouterModelRegistry.post("/searchModels")
async def searchModels(request: Request):
    body = await request.json()
    search = body.get("search", {})
    _type = body.get("type", "findMany")
    result = search_models(search, _type)
    return json.loads(JSONEncoder().encode(result))


@jrjRouterModelRegistry.post("/searchModelsCommon")
async def searchModelsCommon(request: Request):
    body = await request.json()
    result = search_models_common(body)
    return json.loads(JSONEncoder().encode(result))


@jrjRouterModelRegistry.post("/findModelById")
async def find_model_by_id_endpoint(request: Request):
    body = await request.json()
    try:
        _id = ObjectId(body["id"])
    except (KeyError, InvalidId):
        raise HTTPException(status_code=400, detail="Invalid or missing ID")

    result = find_model_by_id(str(_id))
    if not result:
        raise HTTPException(status_code=404, detail="Model not found")
    return json.loads(JSONEncoder().encode(result))


@jrjRouterModelRegistry.post("/updateModelById")
async def updateModelById(request: Request):
    body = await request.json()
    try:
        _id = ObjectId(body["id"])
    except (KeyError, InvalidId):
        raise HTTPException(status_code=400, detail="Invalid or missing ID")

    update_data = body.get("updateObj", {})
    success = update_model(str(_id), update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found or not updated")

    result = find_model_by_id(str(_id))
    if not result:
        raise HTTPException(status_code=404, detail="Model not found")
    return json.loads(JSONEncoder().encode(result))


@jrjRouterModelRegistry.post("/deleteModelById")
async def deleteModelById(request: Request):
    body = await request.json()
    id = body.get("id")
    if not id:
        raise HTTPException(status_code=400, detail="Missing id")
    model = find_model_by_id(str(id))
    if not model:
        raise HTTPException(status_code=404, detail="model not found")
    s3Url = model.get('s3Url')
    if s3Url:
        deleteAJrjModelAsset(s3Url)

    # return json.loads(JSONEncoder().encode(model))

    success = delete_model(id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"deleted": True}




@jrjRouterModelRegistry.post("/selectModel")
async def selectModel(request: Request):
    body = await request.json()
    orderby = body.get('orderBy', [
        {"createdAt": "desc"}
    ])
    result = search_models_common({
        "search": {
            "orderBy": orderby,
            "where": body['where'],
            "pagination": {
                "page": 1,
                "size": 1000
            }
        }
    })
    if not result['data'][0]:
        raise HTTPException(status_code=404, detail="Model not found")
    return json.loads(JSONEncoder().encode(result['data'][0]))


@jrjRouterModelRegistry.post("/selectModelAndPredict")
async def selectModelAndPredict(request: Request):
    result = await selectModel(request)
    modelObj = find_model_by_idAndLoadModel(result['_id'])
    model = loadAJrjModel(modelObj)
    request_body_bytes = await request.json()
    transformedData = await model.transformer(**request_body_bytes['data'])


    return model.mainPredictor(transformedData)

@jrjRouterModelRegistry.post("/selectDfModelAndReturnFirstItem")
async def selectDfModelAndReturnFirstItem(request: Request):
    result = await selectModel(request)
    modelObj = find_model_by_idAndLoadModel(result['_id'])
    model = loadAJrjModel(modelObj)
    return {
        "message": "ok",
        "dfFirstItem": model.df.iloc[0].to_dict()
    }

