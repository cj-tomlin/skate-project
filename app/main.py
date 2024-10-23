import os
import webbrowser

import uvicorn
from starlette.middleware.cors import CORSMiddleware

import config

from fastapi import FastAPI

###################################################################
## Initialise FastAPI session
###################################################################

app = FastAPI(title="Skate Backend", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Application running"}


if __name__ == "__main__":
    print(f"CWD = {os.getcwd()}")
    webbrowser.open(f"http://{config.HOSTNAME}:{config.PORT}/docs")
    uvicorn.run("main:app", host=config.HOSTNAME, port=config.PORT)
