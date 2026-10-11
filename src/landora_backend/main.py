from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from landora_backend.api.router import api_router


app = FastAPI(
    title="Landora API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")