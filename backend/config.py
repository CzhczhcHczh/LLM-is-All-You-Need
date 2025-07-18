"""
Configuration management for Job Planner Assistant.
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(default="sqlite:///./data/database.db", env="DATABASE_URL")
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY", description="OpenAI API key")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE", description="OpenAI API base URL")
    serper_api_key: str = Field(default="", env="SERPER_API_KEY", description="Serper API key for web search")
    
    # ChromaDB
    chromadb_path: str = Field(default="./data/chromadb", env="CHROMADB_PATH")
    
    # Application
    debug: bool = Field(default=True, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # LLM Models Configuration
    phase1_model: str = Field(default="gpt-3.5-turbo", env="PHASE1_MODEL")
    phase2_model: str = Field(default="gpt-3.5-turbo", env="PHASE2_MODEL")
    phase3_model: str = Field(default="gpt-3.5-turbo", env="PHASE3_MODEL")
    phase4_models: str = Field(default="gpt-3.5-turbo,claude-3-haiku,deepseek-v3", env="PHASE4_MODELS")
    
    @property
    def phase4_models_list(self) -> List[str]:
        """Get Phase 4 models as a list."""
        return [model.strip() for model in self.phase4_models.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()

