import os

from database import DatabaseClient, convert_to_en_us_url

from dotenv import load_dotenv
from azure.storage.queue import QueueServiceClient
from fastapi import FastAPI, HTTPException
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
# TODO: フロントエンドのURLを環境変数から取得する必要がありそう
# FRONT_API_URL = os.getenv("FRONT_API_URL")
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
                # TODO: GitHubのリポジトリからダウンロードする必要がある
                content = ""
                # TODO: ダウンロードしたファイルをローカルの/static/templates/に保存する
                # with open("static/templates/main.json", "w") as f:
                #     f.write(content)
                # TODO: パブリックなURLを組み立てて返す
                url = f"{FRONT_API_URL}/static/templates/main.json"
                return {"status": "completed", "url": result.stored_url}
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
