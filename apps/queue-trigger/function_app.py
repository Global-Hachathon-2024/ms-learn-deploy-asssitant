import logging
import os
import json

import azure.functions as func
from dotenv import load_dotenv
import requests

load_dotenv()
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
WORKER_API_URL = os.getenv("WORKER_API_URL")
app = func.FunctionApp()

@app.queue_trigger(arg_name="msg", 
                queue_name="job-queue",
                connection=AZURE_STORAGE_CONNECTION_STRING) 
def queue_trigger(msg: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                msg.get_body().decode('utf-8'))
    try:
        target_url = get_target_url(msg)
        res = requests.post(f"{WORKER_API_URL}/templates", params={"url": target_url})
        logging.info(res.text)
    except Exception as e:
        logging.error(e)

def get_target_url(msg: func.QueueMessage) -> str:
    data = msg.get_json()
    if data["target_url"]:
        return data["target_url"]
    else:
        raise ValueError("No target_url provided")