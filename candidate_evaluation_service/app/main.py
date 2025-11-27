from fastapi import FastAPI
from app.api.routes import router
from app.core.logger import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="Candidate Evaluation Service",
    description="Microservice for AI-powered candidate evaluation using LangGraph",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
