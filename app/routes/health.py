# ---------------------------------------------------------------------------
# app/routes/health.py
# Define a rota de health check da API.
# ---------------------------------------------------------------------------
from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health", summary="Verifica a saúde da API")
def get_health():
    return {"status": "API está operacional"}
