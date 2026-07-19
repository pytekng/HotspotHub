from fastapi import FastAPI

app = FastAPI(
    title="HotspotHub API",
    version="0.1.0",
    description="Backend API for HotspotHub"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to HotspotHub 🚀",
        "status": "running",
        "version": "0.1.0"
    }
