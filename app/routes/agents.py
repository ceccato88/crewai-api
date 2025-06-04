# ---------------------------------------------------------------------------
# app/routes/agents.py
# Define as rotas da API relacionadas aos agentes/crews.
# ---------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field as PydanticField
from crew.crew_executor import execute_crew
from typing import Optional
import logging

logger_agents = logging.getLogger(__name__)

class CreateCrewRequest(BaseModel):
    crew_name: str = PydanticField(..., description="Nome do crew a ser executado (ex: 'basic', 'advanced').", example="basic")
    message: str = PydanticField(..., example="Qual o status do meu pedido XYZ?")
    user_id: str = PydanticField(..., example="user_abc_123")
    session_id: str = PydanticField(..., example="session_xyz_789")
    history_limit: Optional[int] = PydanticField(10, ge=1, le=50, description="Número de mensagens do histórico da sessão a serem recuperadas.", example=5)


agents_router = APIRouter()

@agents_router.post("/create_crew/")
async def create_crew_endpoint(request: CreateCrewRequest):
    logger_agents.info(f"Recebida requisição para /create_crew/: crew_name='{request.crew_name}', user_id='{request.user_id}', session_id='{request.session_id}'")
    try:
        result = await execute_crew(
            crew_name=request.crew_name,
            inputs={"message": request.message},
            user_id=request.user_id,
            session_id=request.session_id,
            history_limit=request.history_limit
        )
        logger_agents.info(f"Crew '{request.crew_name}' para user_id='{request.user_id}', session_id='{request.session_id}' finalizado com sucesso.")
        return {
            "status": "success",
            "message": f"Crew '{request.crew_name}' executado com sucesso com memória Zep!",
            "result": result
        }
    except ValueError as ve:
        logger_agents.warning(f"Erro de valor ao tentar executar crew '{request.crew_name}': {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger_agents.error(f"Erro ao executar crew '{request.crew_name}' para user_id='{request.user_id}', session_id='{request.session_id}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar sua solicitação para o crew '{request.crew_name}'.")
