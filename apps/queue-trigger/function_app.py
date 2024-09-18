import logging
import os
import azure.functions as func
from dotenv import load_dotenv
import requests

load_dotenv()
WORKER_API_URL = os.getenv("WORKER_API_URL")
app = func.FunctionApp()

@app.function_name(name="QueueTrigger")
@app.queue_trigger(arg_name="msg", 
                queue_name="job-queue",
                connection="Storage") 
def queue_trigger(msg: func.QueueMessage):
    url = msg.get_body().decode('utf-8')
    print(f"Python Queue trigger processed a message: {url}")
    try:
        res = requests.post(f"{WORKER_API_URL}/templates", params={"url": url})
        logging.info('Worker API response: %s', res.text)
    except Exception as e:
        logging.error(e)
