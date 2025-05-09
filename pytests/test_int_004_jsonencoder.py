import json
import datetime
import pytest
from bson import ObjectId

from jrjModelRegistry.mongo import JSONEncoder



def test_json_encoder_objectid():
    obj_id = ObjectId("64a1f6f3e43f3f3b9d3cf0a0")
    result = json.dumps({"_id": obj_id}, cls=JSONEncoder)
    assert '"64a1f6f3e43f3f3b9d3cf0a0"' in result


def test_json_encoder_datetime():
    dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
    result = json.dumps({"createdAt": dt}, cls=JSONEncoder)
    assert '"2024-01-01T12:00:00"' in result


def test_json_encoder_fallback():
    class Custom:
        def __str__(self):
            return "custom"

    with pytest.raises(TypeError):
        # Default encoder should fail for unsupported custom objects
        json.dumps({"x": Custom()}, cls=JSONEncoder)
