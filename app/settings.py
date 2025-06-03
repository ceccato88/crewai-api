# ---------------------------------------------------------------------------
# app/settings.py
# Define as configurações da aplicação usando Pydantic BaseSettings.
# ---------------------------------------------------------------------------
from typing import List, Optional
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings # Classe base para configurações carregadas do ambiente

class ApiSettings(BaseSettings):
    # Define os campos de configuração com valores padrão
    title: str = "CrewAI API with Zep Memory"
    version: str = "1.1" # Versão atualizada da API
    docs_enabled: bool = True # Controla se a documentação (Swagger/ReDoc) está habilitada
    # Lista opcional de origens CORS; validação padrão habilitada
    cors_origin_list: Optional[List[str]] = Field(None, validate_default=True)

    @field_validator("cors_origin_list", mode="before") # Validador Pydantic
    @classmethod # O método não depende da instância, então é um classmethod
    def set_cors_origin_list(cls, cors_origin_list, info: ValidationInfo):
        """
        Define a lista de origens CORS padrão se nenhuma for fornecida.
        Garante que as origens padrão (localhost) estejam presentes.
        """
        valid_cors = cors_origin_list or [] # Usa a lista fornecida ou uma lista vazia
        default_origins = ["http://localhost", "http://localhost:3000"] # Origens padrão
        for origin in default_origins:
            if origin not in valid_cors:
                valid_cors.append(origin) # Adiciona origens padrão se não estiverem presentes
        # Garante unicidade (converte para set e de volta para list)
        return list(set(valid_cors))

api_settings = ApiSettings() # Cria uma instância das configurações