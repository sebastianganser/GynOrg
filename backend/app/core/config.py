"""
Application configuration settings.
"""
from typing import List, Optional, Any, Dict
from pydantic_settings import BaseSettings
from pydantic import validator
import os


# Resolve absolute path to backend directory (parent of app/core/config.py is app/core, parent is app, parent is backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Enforce the single source of truth: backend/data/gynorg.db
# (Fallback if no DATABASE_URL is found in .env)
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/gynorg"

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Info
    PROJECT_NAME: str = "GynOrg DEBUG"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database Components
    DB_HOST: Optional[str] = None
    DB_PORT: str = "5432"
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    DATABASE_URL: str = DEFAULT_DATABASE_URL
    DATABASE_ECHO: bool = False
    TEST_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/test_gynorg"

    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v != DEFAULT_DATABASE_URL:
            return v.strip('"').strip("'")
        
        db_host = values.get("DB_HOST")
        if db_host:
            db_user = values.get("DB_USER")
            db_password = values.get("DB_PASSWORD")
            db_port = values.get("DB_PORT", "5432")
            db_name = values.get("DB_NAME")
            if all([db_user, db_password, db_name]):
                return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return DEFAULT_DATABASE_URL

    @validator("TEST_DATABASE_URL", pre=True, always=True)
    def assemble_test_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v != "postgresql://postgres:postgres@localhost:5432/test_gynorg":
            return v
        
        db_host = values.get("DB_HOST")
        if db_host:
            db_user = values.get("DB_USER")
            db_password = values.get("DB_PASSWORD")
            db_port = values.get("DB_PORT", "5432")
            db_name = values.get("DB_NAME")
            if all([db_user, db_password, db_name]):
                return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}_test"
        return "postgresql://postgres:postgres@localhost:5432/test_gynorg"
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production-12345678901234567890"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Authentication (Single User)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:5174"
    
    def get_cors_origins(self) -> List[str]:
        """Convert comma-separated CORS origins to list."""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Container Settings
    CONTAINER_PORT: int = 8000
    CONTAINER_HOST: str = "0.0.0.0"
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30
    
    # AI API Keys (Optional for backend core)
    OPENROUTER_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # Holiday Management Settings
    HOLIDAY_YEARS_PAST: int = 2
    HOLIDAY_YEARS_FUTURE: int = 3
    HOLIDAY_AUTO_IMPORT_ON_STARTUP: bool = True
    HOLIDAY_SCHEDULER_ENABLED: bool = True
    HOLIDAY_SCHEDULER_CRON: str = "0 2 1 * *"
    HOLIDAY_CLEANUP_OLD_YEARS: bool = False
    HOLIDAY_CLEANUP_YEARS_THRESHOLD: int = 5
    
    def get_holiday_year_range(self) -> tuple[int, int]:
        """
        Calculate the holiday year range based on current year and configuration.
        
        Returns:
            tuple: (start_year, end_year)
            
        Example:
            If current year is 2025, HOLIDAY_YEARS_PAST=2, HOLIDAY_YEARS_FUTURE=3:
            Returns (2023, 2028)
        """
        from datetime import datetime
        current_year = datetime.now().year
        start_year = current_year - self.HOLIDAY_YEARS_PAST
        end_year = current_year + self.HOLIDAY_YEARS_FUTURE
        return start_year, end_year
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
