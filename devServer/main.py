

import copy
import sys
import os

from dotenv import load_dotenv

from pathlib import Path

env_path = Path(".env-live")


if env_path.exists():
    # print('asdasdad')
    load_dotenv(dotenv_path=env_path)


else:
    load_dotenv()

from fastapi import FastAPI

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)

from jrjModelRegistry import handleDashboard, jrjRouterModelRegistry,jrjModelRegistryConfig

# originalConfig = copy.deepcopy(jrjModelRegistryConfig)
# print(originalConfig)

app = FastAPI()



app.include_router(jrjRouterModelRegistry)

handleDashboard(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}