import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from generate import BicepDeployer
from database import DatabaseClient, convert_to_en_us_url
from utils.parse import extract_code_blocks
from utils.azcommand import deploy_bicep
from utils.filesys import save_files, create_directory_from_url
from utils.repository import push_to_github
from utils.web_scraper import scrape_web_content

load_dotenv()
BICEP_FILE = os.environ.get("BICEP_FILE")
PARAMETERS_FILE = os.environ.get("PARAMETERS_FILE")

app = FastAPI()
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
db_client = DatabaseClient(conn_str)

MAX_RETRIES = 3

# just for health check
@app.get("/ping")
async def ping():
    return "pong"

@app.post("/templates")
async def generate_handler(url: str):
    try:
        result = db_client.get(url)
    except Exception as e:
        handle_error(500, "Failed to get a result from the database", internal_msg=str(e))

    try:
        completed_valid = not result.in_progress and result.is_valid
        if completed_valid:
            db_client.finish(url, is_valid=False)
            handle_error(400, "The URL is already processed")
        not_completed_valid = result.in_progress and result.is_valid
        if not_completed_valid:
            db_client.finish(url, is_valid=False)
            handle_error(500, "The database is in an inconsistent state")
    except Exception as e:
        handle_error(500, "Failed to update a result in the database", internal_msg=str(e))

    try:
        url = convert_to_en_us_url(url)
        directory_path = create_directory_from_url(url)
        code, content = scrape_web_content(url)
    except Exception as e:
        handle_error(500, "Failed to scrape a web page", internal_msg=str(e))
    
    try:
        if code != 200:
            if code == 404:
                msg = f"the URL not found: {url}"
                db_client.finish(url, is_valid=False)
                handle_error(404, msg)
            else:
                msg = f"Failed to get a page from {url}"
                db_client.finish(url, is_valid=False)
                handle_error(500, msg)
    except Exception as e:
        handle_error(500, "sucessfully scraped the web page but failed to update a result in the database", internal_msg=str(e))

    try:
        deployer = BicepDeployer()
    except Exception as e:
        db_client.finish(url, is_valid=False)
        handle_error(500, "Failed to create a deployer", internal_msg=str(e))
    
    try:
        success = False
        for i in range(1 + MAX_RETRIES):
            if success:
                break

            if i == 0:
                print("Generating a bicep template")
                output = deployer.generate_bicep_template(content)
            else:
                print(f"Retrying to generate a bicep template: {i}")
                output = deployer.fix_bicep_template(message)

            extracted_files = extract_code_blocks(output)
            # TODO: check if files exist in directory_path
            save_files(directory_path, [BICEP_FILE, PARAMETERS_FILE], extracted_files)

            success, message = deploy_bicep(directory_path)
    except Exception as e:
        db_client.finish(url, is_valid=False)
        handle_error(500, "Failed to generate a bicep template", internal_msg=str(e))

    try:
        if success:
            db_client.finish(url, is_valid=True)
            print(f"Generated ARM template for {url} successfully")
        else:
            db_client.finish(url, is_valid=False)
    except Exception as e:
        db_client.finish(url, is_valid=False)
        handle_error(500, "Failed to update the database", internal_msg=str(e))
    
    bicep_path = f"{directory_path}/{BICEP_FILE}"
    parameters_path = f"{directory_path}/{PARAMETERS_FILE}"
    if not os.path.exists(bicep_path):
        db_client.finish(url, is_valid=False)
        print(f"bicep file not found: {bicep_path}")
        handle_error(500, "Failed to generate a bicep file")
    if not os.path.exists(f"{directory_path}/{PARAMETERS_FILE}"):
        print(f"parameters file not found: {parameters_path}")
        try:
            push_to_github(url, bicep_path, params=None)
            if success:
                return {"status": "valid", "url": url}
            else:
                return {"status": "invalid", "url": url}
        except ValueError as e:
            db_client.finish(url, is_valid=False)
            handle_error(500, "Failed to push the bicep file", internal_msg=str(e))
    else:
        try:
            push_to_github(url, bicep_path, params=parameters_path)
            if success:
                return {"status": "valid", "url": url}
            else:
                return {"status": "invalid", "url": url}
        except:
            db_client.finish(url, is_valid=False)
            handle_error(500, "Failed to push the bicep and parameters files", internal_msg=str(e))


def handle_error(code: int, reponse_msg: str, **kwargs: dict):
    internal_msg = kwargs.get("internal_msg")
    if internal_msg:
        print(internal_msg)
    raise HTTPException(status_code=code, detail=reponse_msg)
