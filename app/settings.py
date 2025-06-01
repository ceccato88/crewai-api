# app/settings.py
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pydantic import ValidationInfo

class ApiSettings(BaseSettings):
    title: str = "CrewAI API"
    version: str = "1.0"
    docs_enabled: bool = True
    cors_origin_list: Optional[List[str]] = Field(None, validate_default=True)

    @field_validator("cors_origin_list", mode="before")
    def set_cors_origin_list(cls, cors_origin_list, info: ValidationInfo):
        valid_cors = cors_origin_list or []
        valid_cors.append("http://localhost")
        valid_cors.append("http://localhost:3000")
        return valid_cors

api_settings = ApiSettings()
