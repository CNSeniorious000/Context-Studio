"""
Centralized configuration management using pydantic-settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIClientSettings(BaseSettings):
    """Configuration for AI API clients."""

    # PPIO API settings
    ppio_api_key: str = Field(default="", description="PPIO API key for certain operations")
    ppio_base_url: str = Field(default="https://api.ppinfra.com/v3/openai", description="PPIO API base URL")

    # Aliyun API settings
    aliyun_api_key: str = Field(default="", description="Aliyun API key for embeddings and operations")
    aliyun_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", description="Aliyun API base URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class ModelSettings(BaseSettings):
    """Configuration for AI models."""

    # Model names
    title_model: str = Field(default="deepseek/deepseek-v3-0324", description="Model used for title generation")
    summarize_model: str = Field(default="deepseek/deepseek-v3-0324", description="Model used for summarization")
    condense_model: str = Field(default="qwen-turbo", description="Model used for text condensing")
    embedding_model: str = Field(default="text-embedding-v4", description="Model used for embeddings")

    # Model parameters
    title_max_tokens: int = Field(default=1024, description="Maximum tokens for title generation")
    title_temperature: float = Field(default=0.0, description="Temperature for title generation")
    summarize_temperature: float = Field(default=0.0, description="Temperature for summarization")
    embedding_dimensions: int = Field(default=1024, description="Embedding dimensions")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class ProcessingSettings(BaseSettings):
    """Configuration for text processing parameters."""

    # Text processing limits
    title_text_limit: int = Field(default=2000, description="Maximum text length for title generation")
    default_token_limit: int = Field(default=100, description="Default token limit for fuzzy search")
    fuzzy_search_chunk_size: int = Field(default=200, description="Chunk size for fuzzy search")
    summarize_process_length: int = Field(default=10000, description="Process length for summarization")
    condense_max_words: int = Field(default=100, description="Maximum words for text condensing")

    # Cache settings
    cache_directory: str = Field(default="cache/chunks", description="Directory for caching chunks")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class AppSettings(BaseSettings):
    """Main application settings."""

    # FastAPI settings
    app_title: str = Field(default="Context Manager Extractor API", description="Application title")
    debug_mode: bool = Field(default=True, description="Enable debug mode")
    cors_enabled: bool = Field(default=True, description="Enable CORS in production")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


# Global configuration instances
ai_client_settings = AIClientSettings()
model_settings = ModelSettings()
processing_settings = ProcessingSettings()
app_settings = AppSettings()
