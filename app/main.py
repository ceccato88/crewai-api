# ---------------------------------------------------------------------------
# app/main.py
# Ponto de entrada da aplicação FastAPI, configuração de middlewares e rotas.
# ---------------------------------------------------------------------------
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Para autenticação Bearer
from starlette.middleware.cors import CORSMiddleware # Para habilitar CORS
from app.routes.v1_router import v1_router # Roteador para a versão v1 da API
from app.settings import api_settings # Configurações da API
from app.routes.health import health_router # Roteador para o health check

security = HTTPBearer() # Instância do esquema de segurança Bearer
BEARER_TOKEN = os.getenv("BEARER_TOKEN") # Carrega o token Bearer das variáveis de ambiente

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica se o token de autorização fornecido é válido.
    Levanta HTTPException se o token estiver ausente, inválido ou se o BEARER_TOKEN não estiver configurado.
    """
    if not BEARER_TOKEN:
        # Erro crítico se o token do servidor não estiver configurado
        logger.critical("BEARER_TOKEN não configurado no servidor!") # Adicionar logger se desejar
        raise HTTPException(status_code=500, detail="Configuração de autenticação incompleta no servidor.")
    if authorization.credentials != BEARER_TOKEN:
        # Token fornecido pelo cliente não corresponde ao token esperado
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")
    return authorization.credentials # Retorna as credenciais se o token for válido

def create_app() -> FastAPI:
    """
    Cria e configura a instância da aplicação FastAPI.
    """
    app_instance: FastAPI = FastAPI(
        title=api_settings.title, # Título da API (de settings.py)
        version=api_settings.version, # Versão da API (de settings.py)
        # Habilita/desabilita URLs de documentação com base em settings.py
        docs_url="/docs" if api_settings.docs_enabled else None,
        redoc_url="/redoc" if api_settings.docs_enabled else None,
        openapi_url="/openapi.json" if api_settings.docs_enabled else None,
    )

    # Inclui a rota de health check (pública, sem autenticação)
    app_instance.include_router(health_router, tags=["Health"])

    # Inclui as rotas da v1, protegidas pela função verify_token
    app_instance.include_router(v1_router, dependencies=[Depends(verify_token)])

    # Adiciona o middleware CORS para permitir requisições de diferentes origens
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origin_list, # Lista de origens permitidas (de settings.py)
        allow_credentials=True, # Permite credenciais (cookies, cabeçalhos de autorização)
        allow_methods=["*"], # Permite todos os métodos HTTP (GET, POST, etc.)
        allow_headers=["*"], # Permite todos os cabeçalhos HTTP
    )

    return app_instance # Retorna a instância configurada do FastAPI

app = create_app() # Cria a instância da aplicação que será usada pelo Uvicorn