import os, uuid, re
import datetime

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy
from database import DatabaseClient, Result
from fastapi import FastAPI, Request
import asyncio

app = FastAPI()

# Azure Storage の接続文字列
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
queue_name = "hackathon2024queue"
queue_service_client = QueueServiceClient.from_connection_string(connection_string)
queue_client = queue_service_client.get_queue_client(queue_name)


def convert_to_en_us_url(url):
    converted_url = re.sub(r'(https://learn\.microsoft\.com/)([^/]+/)', r'\1en-us/', url)
    return converted_url

@app.get("/poll_status")
async def poll_status(url: str):
    url = convert_to_en_us_url(url)
    result = Result(url, datetime.datetime.now())
    db_client = DatabaseClient(connection_string)

    status = db_client.get_result(result.category, result.url_hash)
    if status == None: # not in database yet
        db_client.insert(result)
        queue_client.send_message(url)
        return {"status": "uninitialized", "url": ""}
    else: 
        if status["inProgress"]: # inprogress
            return {"status": "inProgress", "url": ""}
        else: # already in database 
            if status ["isValid"]:
                return {"status": "completed", "url": status["storedUrl"]}
            else:
                return {"status": "invalid", "url": status["storedUrl"]}
