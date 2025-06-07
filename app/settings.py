# ---------------------------------------------------------------------------
# app/settings.py
# Define as configurações da aplicação usando Pydantic BaseSettings.
# ---------------------------------------------------------------------------
from typing import List, Optional
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

class ApiSettings(BaseSettings):
    title: str = "CrewAI API with Zep Memory"
    version: str = "1.1"
    docs_enabled: bool = True
    cors_origin_list: Optional[List[str]] = Field(None, validate_default=True)

    @field_validator("cors_origin_list", mode="before")
    @classmethod
    def set_cors_origin_list(cls, cors_origin_list, info: ValidationInfo):
        valid_cors = cors_origin_list or []
        default_origins = ["http://localhost", "http://localhost:3000"]
        for origin in default_origins:
            if origin not in valid_cors:
                valid_cors.append(origin)
        return list(set(valid_cors))

api_settings = ApiSettings()
