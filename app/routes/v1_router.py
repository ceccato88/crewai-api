# ---------------------------------------------------------------------------
# app/routes/v1_router.py
# Agrupa todas as rotas da versão v1 da API.
# ---------------------------------------------------------------------------
from fastapi import APIRouter
from app.routes.agents import agents_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(agents_router, tags=["Crews"])
