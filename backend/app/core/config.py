from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application configuration management.
    Reads from environment variables or a .env file.
    """
    app_name: str = "Plum Health Insurance Claims System"
    environment: str = "development" # development, staging, production
    log_level: str = "INFO"
    
    # AI Config
    gemini_api_key: Optional[str] = None
    flash_model: str = "gemini-2.5-flash"  # Updated for Classification/Verification
    pro_model: str = "gemini-2.5-pro"      # Updated for heavy OCR Extraction
    
    # System Config
    confidence_penalty_per_failure: float = 0.15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()