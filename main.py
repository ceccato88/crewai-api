# ---------------------------------------------------------------------------
# main.py
# Arquivo principal para iniciar a aplicação FastAPI com Uvicorn.
# ---------------------------------------------------------------------------
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
