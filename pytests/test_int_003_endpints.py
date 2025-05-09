# test_mlModelSaver.py

import sys
import os
from dotenv import load_dotenv
import pytest
load_dotenv()

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


def test_ping():
    response = client.get("/jrjModelRegistry/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to JRJ Model Registry"}

