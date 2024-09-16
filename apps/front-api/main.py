import os, uuid
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

inprogress_flag = False


@app.get("/poll_status")
async def poll_status(url: str):

    result = Result(url, datetime.datetime.now())
    db_client = DatabaseClient(connection_string)

    status = db_client.get_result(result.category, result.url_hash)
    if status == None:
        # no database yet
        db_client.upsert(result)
        queue_client.send_message(url)
        print(f"Recieved request. Now sent request to queue")
        db_client.update_db(result.category, result.url_hash, "inProgress", 1)
        return {"status": "uninitialized", "url": ""}
    else:
        if status["inProgress"]:
            return {"status": "inProgress", "url": ""}
        else: # already in database -> return url
            return {"status": "completed", "url": status["storedUrl"]}
