# app/routes/health.py
from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
def get_health():
    """Rota pública para verificar se a API está viva."""
    return {"status": "success"}
