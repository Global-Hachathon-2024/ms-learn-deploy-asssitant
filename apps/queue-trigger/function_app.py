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
        url = get_url(msg)
        res = requests.post(f"{WORKER_API_URL}/templates", params={"url": url})
        logging.info(res.text)
    except Exception as e:
        logging.error(e)

def get_url(msg: func.QueueMessage) -> str:
    url = msg.get_body().decode('utf-8')
    if url == "":
        raise ValueError("No URL provided")
    return url