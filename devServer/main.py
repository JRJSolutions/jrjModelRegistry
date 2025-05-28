from fastapi import FastAPI

import sys
import os

from dotenv import load_dotenv

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

from jrjModelRegistry import handleDashboard, jrjRouterModelRegistry

app = FastAPI()



app.include_router(jrjRouterModelRegistry)

handleDashboard(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}