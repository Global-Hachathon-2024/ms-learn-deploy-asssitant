import os
import re
from pathlib import Path

from github import Github, Auth, Repository

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
    bicep_true_name = 'main.bicep'
    params_true_name = 'main.parameters.json'

    abspath = os.path.abspath(bicep)
    if not abspath.endswith(bicep_true_name):
        raise ValueError(f'Invalid file extension. The file name must be {bicep_true_name}, but {abspath}')
    if not os.path.exists(abspath):
        raise FileNotFoundError(f'The file {abspath} does not exist')
    
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_user(repo_owner).get_repo(repo_name)

    try:
        push(repo, bicep, url)
    except:
        print('Failed to push the bicep file')
        raise ValueError('Failed to push the bicep file')

    if params != None:
        try:
            abspath = os.path.abspath(params_true_name)
            if not abspath.endswith('main.parameters.json'):
                raise ValueError(f'Invalid file extension. The file name must be {params_true_name}, but {abspath}')
            if not os.path.exists(abspath):
                raise FileNotFoundError(f'The file {abspath} does not exist')
            push(repo, params, url)
        except:
            print('Failed to push the parameters file')
            raise ValueError('Failed to push the parameters file')

    g.close()

def push(repo: Repository, path: str, url: str) -> None:
    with open(path, 'r') as file:
        content = file.read()
    stored_dir = make_stored_path(url)
    filename = Path(path).name
    full_path = f'templates/{stored_dir}/{filename}'
    commit_message = f'generate a {filename} automatically for {url}'

    try:
        contents = repo.get_contents(full_path)
        print(f"the file {full_path} already exists and will be updated")
        repo.update_file(full_path, commit_message, content, contents.sha)
    except:
        contents = None
        print(f"the file {full_path} does not exist and will be created")
        repo.create_file(full_path, commit_message, content)

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
