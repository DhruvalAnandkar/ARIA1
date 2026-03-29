from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to mobile app origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
