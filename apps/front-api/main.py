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

@app.post("/enqueue")
async def enqueue_message(url):
    queue_client.send_message(url)
    return {"status": "Message enqueued", "message": url}


@app.get("/poll_status")
async def poll_status(url: str):
    global inprogress_flag

    result = Result(url, datetime.datetime.now())
    db_client = DatabaseClient(connection_string)

    status = db_client.get_result(result.category, result.url_hash)
    if status == None:
        # no database yet
        db_client.upsert(result)
        queue_client.send_message(url)
        print(f"Recieved request. Now sent request to queue")
        db_client.update_db(result.category, result.url_hash, "inProgress", 1)
        inprogress_flag = True
    else:
        # already in database -> return url
        return f'Code: {status["storedUrl"]}'

    # database になかった場合、status["inProgress"] == False になるまで待機
    while inprogress_flag == True:    
        status = db_client.get_result(result.category, result.url_hash)    
        if status["inProgress"] == False:
            inprogress_flag = False
        await asyncio.sleep(1)
    
    status = db_client.get_result(result.category, result.url_hash)
    return f'Code: {status["storedUrl"]}'

@app.get("/update")
async def update_data(url: str):
    global inprogress_flag
    result = Result(url, datetime.datetime.now())
    db_client = DatabaseClient(connection_string)
    db_client.update_db(result.category, result.url_hash, "storedUrl", "test_url2")
    db_client.update_db(result.category, result.url_hash, "inProgress", 0)
    return {"status": "Data updated"}
