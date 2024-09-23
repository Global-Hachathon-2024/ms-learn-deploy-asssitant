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
    url = convert_to_en_us_url(url)
    directory_path = create_directory_from_url(url)
    code, content = scrape_web_content(url)
    if code != 200:
        if code == 404:
            msg = f"the URL not found: {url}"
            handle_error(404, msg)
        else:
            msg = f"Failed to get a page from {url}"
            handle_error(500, msg)

    deployer = BicepDeployer()
    success = False
    for i in range(1 + MAX_RETRIES):
        if success:
            break

        if i == 0:
            logging.info("Generating a bicep template")
            output = deployer.generate_bicep_template(content)
        else:
            logging.info(f"Retrying to generate a bicep template: {i}")
            output = deployer.fix_bicep_template(message)

        extracted_files = extract_code_blocks(output)
        # TODO: check if files exist in directory_path
        save_files(directory_path, [BICEP_FILE, PARAMETERS_FILE], extracted_files)

        success, message = deploy_bicep(directory_path)

    if success:
        handle_complete(url, True, directory_path)
    else:
        handle_complete(url, False, directory_path)


# TODO: handle error and response to the client gracefully
def handle_complete(url: str, is_valid: bool, src_dir: str):
    """
    Handle the completion of generating an ARM template
    Args:
        url (str): URL of the page
        is_valid (bool): Whether the generated template is valid or not
        src_dir (str): Directory path of the generated bicep and parameters files
    """
    logging.info(f"Generated ARM template for {url} successfully")
    db_client.finish(url, is_valid)

    bicep_path = f"{src_dir}/{BICEP_FILE}"
    parameters_path = f"{src_dir}/{PARAMETERS_FILE}"
    if not os.path.exists(bicep_path):
        logging.error(f"bipec file not found: {bicep_path}")
        handle_error(500, "Failed to generate a bicep file")
    if not os.path.exists(f"{src_dir}/{PARAMETERS_FILE}"):
        logging.error(f"parameters file not found: {parameters_path}")
        try:
            push_to_github(url, bicep_path, params=None)
        except ValueError as e:
            handle_error(500, "Failed to push the bicep file", internal_msg=str(e))
    else:
        try:
            push_to_github(url, bicep_path, params=parameters_path)
        except:
            handle_error(500, "Failed to push the bicep and parameters files", internal_msg=str(e))

def handle_error(code: int, reponse_msg: str, **kwargs: dict):
    internal_msg = kwargs.get("internal_msg")
    if internal_msg:
        logging.error(internal_msg)
    raise HTTPException(status_code=code, detail=reponse_msg)