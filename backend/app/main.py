from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.api.routes import router as claims_router
from backend.app.core.config import settings
import os

app = FastAPI(
    title=settings.app_name,
    description="Intelligent Health Insurance Claims Processing Engine",
    version="1.0.0"
)

# 1. FIX CORS: No wildcards allowed when credentials=True
#origins = [
   # "http://localhost:5173",     # Vite local dev
  #  "http://localhost:3000",     # Alternate local dev
   # "https://health-insurance-claims-system.vercel.app", # <-- UPDATE THIS with your actual Vercel URL
#]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://health-insurance-claims-system.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. FIX IMAGES: Serve the uploaded files so Vercel can fetch them
os.makedirs("temp_uploads", exist_ok=True)
app.mount("/temp_uploads", StaticFiles(directory="temp_uploads"), name="temp_uploads")

app.include_router(claims_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}