# ---------------------------------------------------------------------------
# app/routes/agents.py
# Define as rotas da API relacionadas aos agentes/crews.
# ---------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field as PydanticField # Renomeia Field para evitar conflito com o Field do Pydantic
from crew.basic_crew.main import run_async # Função principal para executar o crew
import logging # Módulo de logging

logger_agents = logging.getLogger(__name__) # Logger específico para este módulo de rotas

class CreateCrewRequest(BaseModel):
    """
    Modelo Pydantic para o corpo da requisição da rota /create_crew/.
    Define os campos esperados e seus tipos, com exemplos para documentação.
    """
    message: str = PydanticField(..., example="Olá, qual o status do meu pedido XYZ?")
    user_id: str = PydanticField(..., example="user_abc_123")
    session_id: str = PydanticField(..., example="session_xyz_789")

agents_router = APIRouter() # Cria um roteador FastAPI para as rotas de agentes

@agents_router.post("/create_crew/") # Define uma rota POST
async def create_crew(request: CreateCrewRequest): # Função assíncrona para a rota
    """
    Rota assíncrona que:
    1) Recebe um payload {"message": "...", "user_id": "...", "session_id": "..."}.
    2) Chama run_async para disparar o CrewAI com memória Zep.
    3) Retorna status e resultado ou HTTP 500 em caso de erro.
    """
    logger_agents.info(f"Recebida requisição para /create_crew/: user_id={request.user_id}, session_id={request.session_id}")
    try:
        # Chama a função run_async com os dados da requisição
        result = await run_async(
            inputs={"message": request.message}, # Dicionário de inputs para o crew
            user_id=request.user_id,
            session_id=request.session_id
        )
        logger_agents.info(f"Crew para user_id={request.user_id}, session_id={request.session_id} finalizado com sucesso.")
        # Retorna uma resposta de sucesso
        return {
            "status": "success",
            "message": "Crew executado com sucesso com memória Zep!",
            "result": result
        }
    except Exception as e:
        # Captura qualquer exceção durante o processamento
        logger_agents.error(f"Erro ao executar crew para user_id={request.user_id}, session_id={request.session_id}: {str(e)}", exc_info=True)
        # Levanta uma HTTPException com status 500 (Erro Interno do Servidor)
        # Em produção, evite expor str(e) diretamente se contiver informações sensíveis.
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar sua solicitação.")