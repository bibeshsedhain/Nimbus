from fastapi import FastAPI

from app.routes import functions, health

app = FastAPI(
    title="Nimbus Deployment Service",
    description="Upload and execute Python functions in isolated Docker containers",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(functions.router)
