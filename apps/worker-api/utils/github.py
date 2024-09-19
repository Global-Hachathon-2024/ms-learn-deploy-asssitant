import os
import re
from pathlib import Path

from github import Github, Auth

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../.env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo_owner = 'Global-Hachathon-2024'
repo_name = 'msl-autogen-templates'

def push_to_github(url: str, bicep: str, params: str) -> None:
    """
    Push the given bicep file to the GitHub repository
    Args:
        url (str): MS Learn URL for Quick Start
        bicep (str): path to the bicep file
        params (str): path to the main.parameters.json file
    """
    # TODO: commonize the code to push a file to the GitHub repository
    if not bicep.endswith('.bicep'):
        raise ValueError(f'Invalid file extension, {bicep}. Please provide a valid bicep file')
    if not os.path.exists(bicep):
        raise FileNotFoundError('The file does not exist')

    print(f'GITHUB_TOKEN: {GITHUB_TOKEN}')
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_user(repo_owner).get_repo(repo_name)

    with open(bicep, 'r') as file:
        content = file.read()
    
    stored_path = make_stored_path(url)
    full_path = f'templates/{stored_path}/main.bicep'
    commit_message = f'generate a main.bicep automatically for {url}'
    # TODO: if the file already exists, update the file
    repo.create_file(full_path, commit_message, content)

    if params != None:
        if not params.endswith('.json'):
            raise ValueError('Invalid file extension. Please provide a valid json file')
        if not os.path.exists(params):
            raise FileNotFoundError('The file does not exist')

        with open(params, 'r') as file:
            content = file.read()
        full_path = f'templates/{stored_path}/main.parameters.json'
        commit_message = f'generate a main.parameters.json automatically for {url}'
        # TODO: if the file already exists, update the file
        repo.create_file(full_path, commit_message, content)

    g.close()

def make_stored_path(url: str) -> str:
    """
    Generate a stored path from the given URL, which doesn't end with '/'
    Args:
        url (str): MS Learn URL for Quick Start to generate a stored path
    Returns:
        str: stored path
    """
    # input: "https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli%2Cbrowser"
    # output: "azure-functions/create-first-function-cli-python+linux+bash+azure-cli+browser"
    match = re.search(r'azure/(.*)', url)
    if match:
        last_path = match.group(1)
        if '?tabs=' in last_path:
            repos_path, params = last_path.split('?tabs=')
            replaced_params = params.replace(',', '+')
            replaced_params = params.replace('%2C', '+')
            return f"{repos_path}+{replaced_params}"
        else:
            repos_path = last_path
            return f"{repos_path}"
    else:
        raise ValueError(f"Invalid URL: {url}")
