# test_mlModelSaver.py



import sys
import os
from dotenv import load_dotenv
import pytest
from pymongo.errors import OperationFailure

load_dotenv()


import copy



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


# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_errorConnection():
    jrjModelRegistryConfigCopy = {
        **copy.deepcopy(originalConfig),
        "mongoConnection": os.environ['JRJ_MONGODB_MODEL_REGISTRY_RAISE']
    }
    with pytest.raises(OperationFailure) as exc_info:
        JrjModelRegistry(jrjModelRegistryConfigCopy)
        initMongodb()
    # print (str(exc_info.value))
    assert "authentication failed" in str(exc_info.value)
    JrjModelRegistry(originalConfig)
    initMongodb()




def test_newMongoDb():
    JrjModelRegistry(originalConfig)
    initMongodb()

    models = search_models_common({
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

    newRec = new_model({
        "modelName": "test_newMongoDb",
        "version": "1-1"
    })
    model_byId = find_model_by_idAndLoadModel(newRec['_id'])
    update_model( str(newRec['_id']), {"key1": "value1"})
    requestSearch = client.post(
        "/jrjModelRegistry/searchModelsCommon",
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

