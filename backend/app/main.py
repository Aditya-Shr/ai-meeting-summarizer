from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import meetings, action_items, decisions
from app.core.config import settings

app = FastAPI(
    title="AI Meeting Summarizer API",
    description="API for meeting transcription, summarization, and tracking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(action_items.router, prefix="/api/action-items", tags=["action-items"])
app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Meeting Summarizer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 