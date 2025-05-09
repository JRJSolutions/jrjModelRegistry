# test_mlModelSaver.py



import sys
import os
from dotenv import load_dotenv
import pytest
from pymongo.errors import OperationFailure

from jrjModelRegistry.jrjModelRegistry import registerAJrjModel

load_dotenv()


import copy

import pandas as pd

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)

from jrjModelRegistry import JrjModelRegistry, jrjRouterModelRegistry, jrjModelRegistryConfig

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(jrjRouterModelRegistry)
client = TestClient(app)


from jrjModelRegistry import JrjModelRegistry, jrjModelRegistryConfig
from jrjModelRegistry.mongo import find_model_by_id, find_model_by_idAndLoadModel, initMongodb, new_model, search_models, search_models_common, update_model
originalConfig = copy.deepcopy(jrjModelRegistryConfig)



def test_newRegisterModel():
    JrjModelRegistry(originalConfig)
    initMongodb()

    models = search_models_common({
        "search": {
            "where": {
                "modelName": "test_newRegisterModel",
            },
            "orderBy":  [
                {
                    "modelName": "desc"
                },
                {
                    "_id": "desc"
                }
            ],
            "pagination": {
                "page": 1,
                "size": 5000
            }
        },
    })
    for model in models['data']:
        response = client.post("/jrjModelRegistry/deleteModelById", json={"id": str(model['_id'])})
        res = response.json()
        print(res)

    class ModelData: pass

    model = ModelData()
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['Montreal', 'Toronto', 'Vancouver']
    }

    df = pd.DataFrame(data)
    model.df = df

    config_body = {
        # "modelName":f"test_newRegisterModel",
        # "version":"1",
        "modelType": "data",
        "score": 1,
        "helpers":{},
        "keepLastOnly": True
    }

    with pytest.raises(ValueError) as exc_info:

        model_metadata = registerAJrjModel(model,config_body)
        print(model_metadata)
    assert "modelName" in str(exc_info.value)

    config_body['modelName'] = f"test_newRegisterModel"

    with pytest.raises(ValueError) as exc_info:

        model_metadata = registerAJrjModel(model,config_body)
        print(model_metadata)
    assert "version" in str(exc_info.value)
    config_body['version'] = f"1"

    jrjModelRegistryConfigCopy = {
        **copy.deepcopy(originalConfig),
        "zipPassword": None
    }

    JrjModelRegistry(jrjModelRegistryConfigCopy)
    initMongodb()

    with pytest.raises(OSError) as exc_info:

        model_metadata = registerAJrjModel(model,config_body)
        print(model_metadata)
    assert "zipPassword" in str(exc_info.value)

    JrjModelRegistry(originalConfig)
    initMongodb()

    model_metadata = registerAJrjModel(model,config_body)
    print(model_metadata)
    model_metadata = registerAJrjModel(model,{**config_body, "version": "2"})
    print(model_metadata)

    requestSearch = client.post(
        "/jrjModelRegistry/selectDfModelAndReturnFirstItem",
        json={
            "where": {
                "modelName": "test_newRegisterModel",
            },
            "orderBy":  [
                {
                    "modelName": "desc"
                },
                {
                    "_id": "desc"
                },
            ],
        }
    )
    result = requestSearch.json()
    print(result)

    async def transformer(test = None):
        return test
    def mainPredictor(x):
        return x

    model.transformer = transformer
    model.mainPredictor = mainPredictor

    model_metadata = registerAJrjModel(model,{**config_body, "version": "3"})
    print(model_metadata)

    requestSearch = client.post(
        "/jrjModelRegistry/selectModelAndPredict",
        json={
            "where": {
                "modelName": "test_newRegisterModel",
            },
            "orderBy":  [
                {
                    "modelName": "desc"
                },
                {
                    "_id": "desc"
                },
            ],
            "data": {"test": "test"}
        },
    )
    result = requestSearch.json()
    print(result)
    requestSearch = client.post(
        "/jrjModelRegistry/selectModelAndPredict",
        json={
            "where": {
                "modelName": "test_newRegisterModel",
            },
            "orderBy":  [
                {
                    "modelName": "desc"
                },
                {
                    "_id": "desc"
                },
            ],
            "data": {"test": "test"}
        },
    )
    result = requestSearch.json()
    print(result)

    response = client.post("/jrjModelRegistry/deleteModelById", json={"id": str(model_metadata['_id'])})
    res = response.json()
    print(res)

    return

    update_model( str(newRec['_id']), {"key1": "value1"})
    requestSearch = client.post(
        "/jrjModelRegistry/searchModels",
        json={
            "search": {
                "where": {
                    "modelName": "test_newMongoDb",
                },
                "orderBy":  [
                    {
                        "modelName": "desc"
                    },
                    {
                        "_id": "desc"
                    },
                    None
                ],
                "pagination": {
                    "page": 1,
                    "size": 5000
                }
            },
            "type": "findMany"
        }
    )
    models = requestSearch.json()
    print(models)
    response = client.post("/jrjModelRegistry/deleteModelById", json={"id": str(newRec['_id'])})
    res = response.json()
    print(res)
    response = client.post("/jrjModelRegistry/deleteModelById", json={"id": str(newRec['_id'])})
    res = response.json()
    print(res)
    response = client.post("/jrjModelRegistry/deleteModelById", json={})
    res = response.json()
    print(res)
    newRec = new_model({
        "modelName": "test_newMongoDb",
        "version": "1-1",
        "s3Url": "asd"
    })
    response = client.post("/jrjModelRegistry/findModelById", json={"id": str(newRec['_id'])})
    res = response.json()
    print(res)
    response = client.post("/jrjModelRegistry/findModelById", json={"id": 'aa'})
    res = response.json()
    print(res)

    requestSearch = client.post(
        "/jrjModelRegistry/selectModel",
        json= {
                "where": {
                    "modelName": "test_newMongoDb",
                },
                "orderBy":  [
                    {
                        "modelName": "desc"
                    },
                    {
                        "_id": "desc"
                    },
                    None
                ],
            }
    )
    models = requestSearch.json()
    print(models)
    update1Req = client.post(
        "/jrjModelRegistry/updateModelById",
        json= {
               "id": str(newRec['_id'])
            }
    )
    update1ReRes = update1Req.json()
    print(update1ReRes)
    update1Req = client.post(
        "/jrjModelRegistry/updateModelById",
        json= {
               "id": 'asdad',
            }
    )
    update1ReRes = update1Req.json()
    print(update1ReRes)

    update2Req = client.post(
        "/jrjModelRegistry/updateModelById",
        json= {
               "id": str(newRec['_id']),
               "updateObj": {
                   "test": '123'
               }
            }
    )
    update1ReRes = update2Req.json()
    print(update1ReRes)

    response = client.post("/jrjModelRegistry/deleteModelById", json={"id": str(newRec['_id'])})
    res = response.json()
    print(res)
    requestSearch = client.post(
        "/jrjModelRegistry/selectModel",
        json= {
                "where": {
                    "modelName": "test_newMongoDb",
                },
                "orderBy":  [
                    {
                        "modelName": "desc"
                    },
                    {
                        "_id": "desc"
                    },
                ],
            }
    )
    models = requestSearch.json()
    print(models)

