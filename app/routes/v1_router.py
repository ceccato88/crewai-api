# app/routes/v1_router.py
from fastapi import APIRouter
from app.routes.health import health_router
from app.routes.agents import agents_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

# Inclui o router de saúde e o router de agentes
v1_router.include_router(health_router)  # Inclui apenas uma vez
v1_router.include_router(agents_router)  # Inclui o router de agentes para /create_crew/
