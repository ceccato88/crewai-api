# ---------------------------------------------------------------------------
# app/routes/health.py
# Define a rota de health check da API.
# ---------------------------------------------------------------------------
from fastapi import APIRouter

health_router = APIRouter() # Cria um roteador FastAPI para o health check

@health_router.get("/health", summary="Verifica a saúde da API") # Define uma rota GET
def get_health():
    """Rota pública para verificar se a API está viva."""
    return {"status": "API está operacional"} # Retorna um status de sucesso simples