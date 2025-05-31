# app/settings.py
from typing import List, Optional
from pydantic import Field, field_validator  # Importando corretamente do pydantic
from pydantic_settings import BaseSettings  # Agora importado de pydantic-settings
from pydantic_core.core_schema import FieldValidationInfo

class ApiSettings(BaseSettings):
    """Configurações da API definidas por variáveis de ambiente"""

    title: str = "CrewAI API"
    version: str = "1.0"

    # Defina como False para desabilitar os docs no /docs e /redoc
    docs_enabled: bool = True

    # Lista de origens CORS permitidas
    cors_origin_list: Optional[List[str]] = Field(None, validate_default=True)

    @field_validator("cors_origin_list", mode="before")  # Decorador de validação de campo
    def set_cors_origin_list(cls, cors_origin_list, info: FieldValidationInfo):
        valid_cors = cors_origin_list or []

        # Adiciona localhost para permitir requisições do ambiente local
        valid_cors.append("http://localhost")
        # Adiciona localhost:3000 para permitir requisições da interface local do Agent UI
        valid_cors.append("http://localhost:3000")

        return valid_cors

# Criar o objeto de configurações da API
api_settings = ApiSettings()
