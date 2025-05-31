# app/main.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes.v1_router import v1_router
from app.settings import api_settings

def create_app() -> FastAPI:
    """Cria a aplicação FastAPI"""
    app: FastAPI = FastAPI(
        title=api_settings.title,
        version=api_settings.version,
        docs_url="/docs" if api_settings.docs_enabled else None,
        redoc_url="/redoc" if api_settings.docs_enabled else None,
        openapi_url="/openapi.json" if api_settings.docs_enabled else None,
    )

    # Adiciona o router v1
    app.include_router(v1_router)

    # Adiciona o Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

# Cria a instância da aplicação FastAPI
app = create_app()
