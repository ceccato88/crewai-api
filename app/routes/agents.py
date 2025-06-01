# app/routes/agents.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from crew.dev_crew.main import run 

class CreateCrewRequest(BaseModel):
    topic: str
    
agents_router = APIRouter()

@agents_router.post("/create_crew/")
async def create_crew(request: CreateCrewRequest):  
    try:
        result = run({"topic": request.topic})
        return {"status": "success", "message": "Crew criado com sucesso!", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar crew: {str(e)}")
