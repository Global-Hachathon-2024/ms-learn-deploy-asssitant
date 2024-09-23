import os

from database import DatabaseClient, convert_to_en_us_url

from dotenv import load_dotenv
from azure.storage.queue import QueueServiceClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    url: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Storage の接続文字列
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
queue_name = "job-queue"
queue_service_client = QueueServiceClient.from_connection_string(connection_string)
queue_client = queue_service_client.get_queue_client(queue_name)

# just for health check
@app.get("/ping")
async def ping():
    return "pong"

@app.get("/poll_status")
async def poll_status(url: str):
    db_client = DatabaseClient(connection_string)
    result = db_client.get(url)
    if result == None: # not in database yet
        return {"status": "uninitialized", "url": ""}
    else: 
        if result.in_progress:
            return {"status": "inProgress", "url": ""}
        else: # already in database 
            if result.is_valid:
                return {"status": "completed", "url": result.stored_url}
            else:
                return {"status": "invalid", "url": result.stored_url}

@app.post("/generate")
async def generate(url_request: GenerateRequest):
    url = url_request.url
    db_client = DatabaseClient(connection_string)
    result = db_client.get(url)
    if result == None:
        db_client.insert(url)
        url = convert_to_en_us_url(url)
        queue_client.send_message(url)
    return {"status": "inProgress", "url": ""}
