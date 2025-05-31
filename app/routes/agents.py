# app/routes/agents.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel  # Importando o Pydantic para validar o corpo da requisição
from src.research_crew.main import run 

# Modelo Pydantic para validar os parâmetros da requisição
class CreateCrewRequest(BaseModel):
    topic: str  # Defina os campos esperados para o input do crew

agents_router = APIRouter()

@agents_router.post("/create_crew/")
async def create_crew(request: CreateCrewRequest):  # Use o modelo para validar os parâmetros
    """Cria e executa o crew de pesquisa, retornando o resultado como resposta HTTP"""
    try:
        # Executa o crew com os parâmetros passados e retorna o resultado
        result = run({"topic": request.topic})  # Passa o parâmetro topic

        # Retorna o resultado como resposta HTTP
        return {"status": "success", "message": "Crew criado com sucesso!", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar crew: {str(e)}")
