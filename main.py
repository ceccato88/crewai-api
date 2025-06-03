# ---------------------------------------------------------------------------
# main.py
# Arquivo principal para iniciar a aplicação FastAPI com Uvicorn.
# ---------------------------------------------------------------------------
import uvicorn
from app.main import app # Importa a instância da aplicação FastAPI

if __name__ == "__main__":
    # Executa o servidor Uvicorn
    # "app.main:app" refere-se ao objeto 'app' no arquivo 'app/main.py'
    # host="0.0.0.0" torna o servidor acessível externamente
    # port=8000 define a porta do servidor
    # reload=True habilita o recarregamento automático durante o desenvolvimento
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
