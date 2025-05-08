# test_mlModelSaver.py

import sys
import os


sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)


from jrjModelRegistry import JrjMlModelRegistry, jrjRouterModelRegistry

def test_test():
    jrjMlReg = JrjMlModelRegistry({})
    res = jrjMlReg.test(1)
    assert res == 1


from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(jrjRouterModelRegistry)
client = TestClient(app)


def test_ping():
    response = client.get("/jrjModelRegistry/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to JRJ Model Registry"}