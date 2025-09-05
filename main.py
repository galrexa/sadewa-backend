from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import patients, icd10, interactions
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SADEWA API",
    description="Smart Assistant for Drug & Evidence Warning",
    version="1.0.0"
)

# CORS setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api", tags=["patients"])
app.include_router(icd10.router, prefix="/api", tags=["icd10"])
app.include_router(interactions.router, prefix="/api", tags=["interactions"])

@app.get("/")
async def root():
    return {
        "message": "SADEWA API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "groq": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)