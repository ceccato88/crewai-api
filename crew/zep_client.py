# ---------------------------------------------------------------------------
# crew/zep_client.py
# Responsável pela inicialização do cliente Zep.
# ---------------------------------------------------------------------------
import os
from zep_cloud.client import AsyncZep
import logging # Adicionado para logar o status da chave ZEP
from typing import Optional

logger_zep_client = logging.getLogger(__name__)

ZEP_API_KEY = os.environ.get("ZEP_API_KEY")
zep_client: Optional[AsyncZep] = None # Tipagem explícita

if not ZEP_API_KEY:
    logger_zep_client.warning("ALERTA: ZEP_API_KEY não está configurada nas variáveis de ambiente. A integração com Zep não funcionará.")
    # zep_client permanece None
else:
    try:
        zep_client = AsyncZep(api_key=ZEP_API_KEY)
        logger_zep_client.info("Cliente Zep inicializado com sucesso.")
    except Exception as e:
        logger_zep_client.error(f"Falha ao inicializar o cliente Zep: {e}", exc_info=True)
        # zep_client permanece None ou pode ser explicitamente setado para None

