import os
import re

from github import Github, Auth

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOSITORY_URL = 'msl-autogen-templates'

def push_to_github(bicep: str, url: str, **kwargs) -> None:
    """
    Push the given bicep file to the GitHub repository
    Args:
        bicep (str): path to the bicep file
        params (str): path to the parameters.json file
        url (str): URL to generate a stored path
    """
    # TODO: commonize the code to push a file to the GitHub repository
    if not bicep.endswith('.bicep'):
        raise ValueError(f'Invalid file extension, {bicep}. Please provide a valid bicep file')
    if not os.path.exists(bicep):
        raise FileNotFoundError('The file does not exist')

    # TODO: use the valid token
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_user().get_repo(REPOSITORY_URL)

    with open(bicep, 'r') as file:
        content = file.read()
    
    stored_path = make_stored_path(url)
    full_path = f'templates/{stored_path}/main.bicep'
    commit_message = f'generate a bicep automatically for {url}'
    repo.create_file(full_path, commit_message, content)

    params = kwargs.get('params')
    if params:
        if not params.endswith('.json'):
            raise ValueError('Invalid file extension. Please provide a valid json file')
        if not os.path.exists(params):
            raise FileNotFoundError('The file does not exist')

        with open(params, 'r') as file:
            content = file.read()
        full_path = f'templates/{stored_path}/parameters.json'
        commit_message = f'generate a parameters.json automatically for {url}'
        repo.create_file(full_path, commit_message, content)

    g.close()

def make_stored_path(url: str) -> str:
    """
    Generate a stored path from the given URL, which doesn't end with '/'
    Args:
        url (str): URL to generate a stored path
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
            return f"{repos_path}+{replaced_params}"
        else:
            repos_path = last_path
            return f"{repos_path}"
    else:
        raise ValueError(f"Invalid URL: {url}")

# TODO: delete the following code
push_to_github(
    './generated/main.bicep', 
    'https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli%2Cbrowser'
)