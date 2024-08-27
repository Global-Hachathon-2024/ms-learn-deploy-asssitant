# main.py
from fastapi import FastAPI

app = FastAPI()

# just for health check
@app.get("/ping")
async def ping():
    return "pong"