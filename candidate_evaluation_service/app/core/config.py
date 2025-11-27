from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str = "openai:gpt-4.1"
    MAX_DEBATE_ROUNDS: int = 2
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
