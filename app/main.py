from fastapi import FastAPI
from app.routes.health import router as health_router

app = FastAPI(
    title="Arealty Crawler API",
    description="Real estate data crawler with scheduled jobs",
    version="1.0.0"
)

# Include routers
app.include_router(health_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)