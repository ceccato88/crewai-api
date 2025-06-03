# ---------------------------------------------------------------------------
# app/routes/v1_router.py
# Agrupa todas as rotas da versão v1 da API.
# ---------------------------------------------------------------------------
from fastapi import APIRouter
# A rota de health agora é pública e registrada em app/main.py, não precisa ser incluída aqui.
from app.routes.agents import agents_router # Importa o roteador de agentes

# Cria um roteador principal para a v1 com um prefixo /v1
v1_router = APIRouter(prefix="/v1")

# Inclui o roteador de agentes no roteador v1
v1_router.include_router(agents_router, tags=["Crews"])