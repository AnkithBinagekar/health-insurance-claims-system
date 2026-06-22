from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as claims_router
from backend.app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Intelligent Health Insurance Claims Processing Engine",
    version="1.0.0"
)

# Allow React frontend (running on Vite's default port 5173) to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}