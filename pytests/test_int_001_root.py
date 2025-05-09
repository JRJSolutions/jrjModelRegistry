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


from jrjModelRegistry import JrjModelRegistry, jrjModelRegistryConfig
from jrjModelRegistry.mongo import initMongodb
originalConfig = copy.deepcopy(jrjModelRegistryConfig)

def test_test1():
    jrjMlReg = JrjModelRegistry(originalConfig)
    res = jrjMlReg.test(1)
    assert res == 1

def test_test2():
    jrjModelRegistryConfigCopy = {
        **copy.deepcopy(originalConfig),
        "s3Endpoint": None
    }
    with pytest.raises(ValueError) as exc_info:
        JrjModelRegistry(jrjModelRegistryConfigCopy)

    assert "s3Endpoint" in str(exc_info.value)
    JrjModelRegistry(originalConfig)


