# main.py
import os
import logging
import datetime

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from generate import generate_arm_template
from validate import validate_arm_template
from database import DatabaseClient, Result

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

    template = generate_arm_template(url)
    result = Result(url, datetime.datetime.now())

    is_valid = validate_arm_template(template)
    if is_valid:
        handle_success(url, result, template)
        return f"ARM template for {url} generated successfully"
    
    logging.info(f"Generated ARM template is invalid")
    
    # TODO: if invalid, get an error message and retry to generate an ARM template with some references
    for i in range(RETRY_CNT):
        logging.info(f"try to generate an ARM template {i+2} times")
        template = generate_arm_template(url)
        result.exec_datetime = datetime.datetime.now()
        is_valid = validate_arm_template(template)
        if is_valid:
            handle_success(url, result, template)
            return f"ARM template for {url} generated successfully"
    handle_error(500, "Failed to generate an ARM template")

def handle_success(url: str, result: Result, template: str):
    logging.info(f"Generated ARM template for {url} successfully")
    result.status = True
    db_client.upsert(result)
    # TODO: save it to our GitHub repository

def handle_error(code, msg):
    logging.error(msg)
    raise HTTPException(status_code=code, detail=msg)

def get_content_from_url(url: str) -> tuple[int, str]:
    response = requests.get(url)
    return response.status_code, response.text
