# app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from app.routes.v1_router import v1_router
from app.settings import api_settings

security = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    if authorization.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")
    return authorization.credentials

def create_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title=api_settings.title,
        version=api_settings.version,
        docs_url="/docs" if api_settings.docs_enabled else None,
        redoc_url="/redoc" if api_settings.docs_enabled else None,
        openapi_url="/openapi.json" if api_settings.docs_enabled else None,
    )

    app.include_router(v1_router, dependencies=[Depends(verify_token)])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_app()
