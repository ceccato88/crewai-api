# app/routes/agents.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from crew.basic_crew.main import run_async

class CreateCrewRequest(BaseModel):
    message: str

agents_router = APIRouter()

@agents_router.post("/create_crew/")
async def create_crew(request: CreateCrewRequest):
    """
    Rota assíncrona que:
    1) Recebe um payload {"message": "..."}.
    2) Chama run_async para disparar o CrewAI.
    3) Retorna status e resultado ou HTTP 500 em caso de erro.
    """
    try:
        result = await run_async({"message": request.message})
        return {
            "status": "success",
            "message": "Crew criado com sucesso!",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar crew: {str(e)}")
