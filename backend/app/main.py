from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.resume import router as resume_router
from app.routers.job_description import router as job_description_router
from app.routers.dashboard import router as dashboard_router
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)
app.include_router(job_description_router)
app.include_router(dashboard_router)

@app.get("/")
async def root():
    return {"message": "✅ AI Resume Analyzer API is running"}