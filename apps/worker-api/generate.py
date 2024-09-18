import os
import re
from pathlib import Path

from dotenv import load_dotenv

from src.azcommand import deploy_bicep
from src.file_io import save_files
from src.llm import BicepDeployer
from src.urls import create_directory_from_url
from src.web_scraper import scrape_web_content

load_dotenv(Path(__file__).parent / "../.env")

MAX_RETRIES = 3


def generate_bicep(url: str) -> str:
    """
    Generate a Bicep file from the given URL
    Args:
        url (str): URL to generate a Bicep file
    Returns:
        str: file path of the generated Bicep file
    """
    directory_path = create_directory_from_url(url)
    # print(f"Directory path: {directory_path}")

    content = scrape_web_content(url)
    print(content)
    # print("==========")

    deployer = BicepDeployer()
    success = False
    for i in range(1 + MAX_RETRIES):
        if success:
            break

        if i == 0:
            output = deployer.generate_bicep_template(content)
        else:
            # print(f"==========\nRetrying... Attempt {i}")
            output = deployer.fix_bicep_template(message)

        extracted_files = extract_code_blocks(output)
        save_files(directory_path, [os.environ.get("BICEP_FILE"), os.environ.get("PARAMETERS_FILE")], extracted_files)

        success, message = deploy_bicep(directory_path)
        # print(message)

    if success:
        return True, directory_path

    return False, directory_path


def extract_code_blocks(text):
    code_block_pattern = re.compile(r'```(azuredeploy\.bicep|azuredeploy\.parameters\.json)\n(.*?)\n```', re.DOTALL)
    matches = code_block_pattern.findall(text)

    extracted_files = {}
    for filename, code in matches:
        # Duplicate filenames may occur but will be overwritten
        extracted_files[filename] = code

    return extracted_files
