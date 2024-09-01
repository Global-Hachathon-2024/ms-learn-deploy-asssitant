import logging
import os

import azure.functions as func
from dotenv import load_dotenv

load_dotenv()
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
app = func.FunctionApp()

@app.queue_trigger(arg_name="msg", 
                queue_name="job-queue",
                connection=conn_str) 
def queue_trigger(msg: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                msg.get_body().decode('utf-8'))
    print("hogehogehoge")
    print("Message: ", msg.get_body().decode('utf-8'))