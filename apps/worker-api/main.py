# main.py
import os
import logging
import datetime

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from generate import generate_bicep
from validate import validate_bicep
from database import DatabaseClient, Result
from push_code import push_to_github

RETRY_CNT = 2

load_dotenv()
app = FastAPI()
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
db_client = DatabaseClient(conn_str)

# just for health check
@app.get("/ping")
async def ping():
    return "pong"

# generate ARM template
@app.post("/templates")
async def generate_handler(url: str):

    code, content = get_content_from_url(url)
    if code == 200:
        logging.info(f"Successfully get a page from {url}")
        logging.debug(content)
    elif code == 404:
        msg = f"URL not found: {url}"
        handle_error(code, msg)
    else:
        msg = f"Failed to get a page from {url}"
        handle_error(500, msg)
    
    generated = generate_bicep(url)
    result = Result(url, datetime.datetime.now())

    is_valid, err_message = validate_bicep(generated)
    if is_valid:
        handle_complete(url, is_valid, generated)
        return f"ARM template for {url} generated successfully"
    
    logging.info(f"Generated ARM template is invalid")
    
    # TODO: if invalid, get an error message and retry to generate an ARM template with some references
    for i in range(RETRY_CNT):
        logging.info(f"try to generate an ARM template {i+2} times")
        generated = generate_bicep(url)
        result.exec_datetime = datetime.datetime.now()
        is_valid, err_message = validate_bicep(generated)
        if is_valid:
            handle_complete(url, is_valid, generated)
            return f"ARM template for {url} generated successfully"
    handle_complete(url, is_valid, generated)
    handle_error(500, "Failed to generate an ARM template")

# TODO: handle error and response to the client gracefully
def handle_complete(url: str, is_valid: bool, bicep: str):
    """
    Handle the completion of generating an ARM template
    Args:
        url (str): URL of the page
        is_valid (bool): Whether the generated template is valid or not
        bicep (str): File path of the generated Bicep file
    """
    logging.info(f"Generated ARM template for {url} successfully")
    db_client.finish(url, is_valid)
    push_to_github(bicep, url)

def handle_error(code, msg):
    logging.error(msg)
    raise HTTPException(status_code=code, detail=msg)

def get_content_from_url(url: str) -> tuple[int, str]:
    response = requests.get(url)
    return response.status_code, response.text
