import os
from pathlib import Path

from database import make_stored_dirpath

from github import Github, Auth, Repository, InputGitAuthor
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../.env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo_owner = 'Global-Hachathon-2024'
repo_name = 'msl-autogen-templates'
github_bot_name = 'github-actions[bot]'
github_bot_email = 'users.noreply.github.com'

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
    push(repo, bicep, url)

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
    stored_dir = make_stored_dirpath(url, is_github_url=False)
    filename = Path(path).name
    full_path = f'{stored_dir}/{filename}'
    commit_message = f'generate a {filename} automatically for {url}'

    contents = None
    try:
        print(f"try to get the file {full_path} from the repository")
        contents = repo.get_contents(full_path)
    except:
        print(f"the file {full_path} does not exist and will be created")
        author=InputGitAuthor(github_bot_email, github_bot_name)
        repo.create_file(
            path=full_path, 
            message=commit_message, 
            content=content,
            branch='main',
            committer=author,
            author=author
        )
    else:
        print(f"the file {full_path} already exists and will be updated")
        author=InputGitAuthor(github_bot_email, github_bot_name)
        repo.update_file(
            path=full_path, 
            message=commit_message, 
            content=content,
            sha=contents.sha,
            branch='main',
            committer=author,
            author=author
        )
