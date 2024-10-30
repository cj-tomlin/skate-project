import os
import webbrowser

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from app.core import config
from fastapi import FastAPI
from app.api.routes import router as api_router

###################################################################
## Initialise FastAPI session
###################################################################

app = FastAPI(title="Skate Backend", version="0.1.0")

# Include API router after the app initialization
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # Restrict this to specific domains in production
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
    ],  # Allow all HTTP methods for now
    allow_headers=["*"],  # Allow all headers for now
)

if __name__ == "__main__":
    print(f"CWD = {os.getcwd()}")
    webbrowser.open(f"http://{config.HOSTNAME}:{config.PORT}/docs")
    uvicorn.run("main:app", host=config.HOSTNAME, port=config.PORT)
