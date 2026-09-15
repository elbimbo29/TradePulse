# config.py
import os
from dotenv import load-dotenv

# Load environment variables from a local .env file
load_dotenv()

class Config:
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def validate(cls):
        missing = []
        if not cls.FINNHUB_API_KEY:
            missing.append("FINNHUB_API_KEY")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate keys immediately on import so the app fails fast if misconfigured
Config.validate()