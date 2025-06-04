# ---------------------------------------------------------------------------
# app/main.py
# Ponto de entrada da aplicação FastAPI, configuração de middlewares e rotas.
# ---------------------------------------------------------------------------
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from app.routes.v1_router import v1_router
from app.settings import api_settings
from app.routes.health import health_router

security = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    if not BEARER_TOKEN:
        raise HTTPException(status_code=500, detail="Configuração de autenticação incompleta no servidor.")
    if authorization.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")
    return authorization.credentials

def create_app() -> FastAPI:
    app_instance: FastAPI = FastAPI(
        title=api_settings.title,
        version=api_settings.version,
        docs_url="/docs" if api_settings.docs_enabled else None,
        redoc_url="/redoc" if api_settings.docs_enabled else None,
        openapi_url="/openapi.json" if api_settings.docs_enabled else None,
    )
    app_instance.include_router(health_router, tags=["Health"])
    app_instance.include_router(v1_router, dependencies=[Depends(verify_token)])
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app_instance

app = create_app()