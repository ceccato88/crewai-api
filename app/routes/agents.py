# ---------------------------------------------------------------------------
# app/routes/agents.py
# Define as rotas da API relacionadas aos agentes/crews.
# ---------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field # Alterado de PydanticField para Field
from crew.crew_executor import execute_crew, ZepSearchScope, ZepReranker # Importa tipos para Zep params
from typing import Optional
import logging
import traceback # Adicionado para obter o traceback completo

logger_agents = logging.getLogger(__name__)

class CreateCrewRequest(BaseModel):
    crew_name: str = Field(..., description="Nome do crew a ser executado (ex: 'basic', 'advanced').", example="basic")
    message: str = Field(..., example="Qual o status do meu pedido XYZ?")
    user_id: str = Field(..., example="user_abc_123")
    session_id: str = Field(..., example="session_xyz_789")
    history_limit: Optional[int] = Field(10, ge=1, le=50, description="Número de mensagens do histórico da sessão a serem recuperadas.", example=5)
    # Parâmetros opcionais para busca no grafo Zep
    zep_graph_search_scope_override: Optional[ZepSearchScope] = Field(None, description="Override para o escopo da busca no grafo Zep ('edges' ou 'nodes').")
    zep_graph_search_reranker_override: Optional[ZepReranker] = Field(None, description="Override para o reranker da busca no grafo Zep.")
    zep_graph_search_limit_override: Optional[int] = Field(None, ge=1, le=20, description="Override para o limite de resultados da busca no grafo Zep.")


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
            history_limit=request.history_limit,
            zep_graph_search_scope_override=request.zep_graph_search_scope_override,
            zep_graph_search_reranker_override=request.zep_graph_search_reranker_override,
            zep_graph_search_limit_override=request.zep_graph_search_limit_override
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
        # Modificação para depuração: incluir mais detalhes do erro na resposta
        tb_str = traceback.format_exc()
        logger_agents.error(f"Erro ao executar crew '{request.crew_name}' para user_id='{request.user_id}', session_id='{request.session_id}': {str(e)}\nTraceback: {tb_str}", exc_info=True) # exc_info=True já loga o traceback
        
        # Preparar detalhes do erro para a resposta HTTP.
        # Em produção, evite expor tracebacks completos ao cliente.
        # Isto é apenas para fins de depuração durante o desenvolvimento.
        detailed_error_info = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback_snippet": tb_str.splitlines()[-5:] # Apenas as últimas 5 linhas para não poluir muito o output do teste
        }
        # O traceback completo ainda será logado no servidor pela linha logger_agents.error acima.
        
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao processar sua solicitação para o crew '{request.crew_name}'. Detalhes de depuração: {detailed_error_info}"
        )
