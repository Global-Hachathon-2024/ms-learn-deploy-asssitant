import os
import requests
import json

from database import DatabaseClient, convert_to_en_us_url
from datetime import datetime

from dotenv import load_dotenv
from azure.storage.queue import QueueServiceClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
FRONT_API_URL = os.getenv("FRONT_API_URL")
queue_name = "job-queue"
queue_service_client = QueueServiceClient.from_connection_string(connection_string)
queue_client = queue_service_client.get_queue_client(queue_name)

STATIC_DIR = "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
                raw_url = convert_to_raw_url(result.stored_url)
                response = requests.get(raw_url)
                data = response.json()

                file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open(f"static/{file_name}.json", "w") as f:
                    f.write(data)
                return_url = f"{FRONT_API_URL}/static/{file_name}.json"
                
                return {"status": "completed", "url": return_url}
            else:
                return {"status": "invalid", "url": result.stored_url}

@app.post("/generate")
async def generate(url_request: GenerateRequest):
    url = url_request.url
    db_client = DatabaseClient(connection_string)
    result = db_client.get(url)
    if result == None:
        print("Result is None so insert the url to the database and send a message to the queue")
        try:
            db_client.insert(url)
        except Exception as e:
            print(f"Failed to insert the url to the database: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to insert the url to the database")
        url = convert_to_en_us_url(url)
        queue_client.send_message(url)
    return {"status": "inProgress", "url": ""}



def convert_to_raw_url(github_url):
    base_url = github_url.replace("https://github.com/", "")
    
    parts = base_url.split("/blob/")
    repo_path = parts[0]
    file_path = parts[-1]
    
    raw_url = f"https://raw.githubusercontent.com/{repo_path}/refs/heads/{file_path}"
    
    return raw_url