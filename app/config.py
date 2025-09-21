import os
from typing import Optional

class Settings:
    """Application settings and configuration."""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # File Paths
    COMPLIANCE_SNIPPETS_PATH: str = os.getenv(
        "COMPLIANCE_SNIPPETS_PATH", 
        "sample_data/compliance_snippets.json"
    )
    
    def __init__(self):
        """Initialize settings and validate required configurations."""
        if not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. LLM functionality will not work.")
    
    def validate(self) -> bool:
        """Validate that all required settings are present."""
        required_settings = [
            ("OPENAI_API_KEY", self.OPENAI_API_KEY),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value:
                missing.append(name)
        
        if missing:
            print(f"Missing required settings: {', '.join(missing)}")
            return False
        
        return True

# Create a singleton instance
settings = Settings()
