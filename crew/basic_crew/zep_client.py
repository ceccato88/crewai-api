# ---------------------------------------------------------------------------
# crew/basic_crew/zep_client.py
# Responsável pela inicialização do cliente Zep.
# ---------------------------------------------------------------------------
import os
from zep_cloud.client import AsyncZep # Cliente assíncrono da Zep

# Obtém a chave da API Zep das variáveis de ambiente
ZEP_API_KEY = os.environ.get("ZEP_API_KEY")

if not ZEP_API_KEY:
    # Emite um alerta se a chave da API não estiver configurada
    print("ALERTA: ZEP_API_KEY não está configurada nas variáveis de ambiente. A integração com Zep não funcionará.")
    zep_client = None # Define o cliente como None se a chave não estiver disponível
else:
    # Inicializa o cliente AsyncZep com a chave da API
    zep_client = AsyncZep(api_key=ZEP_API_KEY)