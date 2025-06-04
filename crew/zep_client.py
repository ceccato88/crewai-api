# ---------------------------------------------------------------------------
# crew/zep_client.py
# Responsável pela inicialização do cliente Zep.
# ---------------------------------------------------------------------------
import os
from zep_cloud.client import AsyncZep

ZEP_API_KEY = os.environ.get("ZEP_API_KEY")

if not ZEP_API_KEY:
    print("ALERTA: ZEP_API_KEY não está configurada nas variáveis de ambiente. A integração com Zep não funcionará.")
    zep_client = None
else:
    zep_client = AsyncZep(api_key=ZEP_API_KEY)