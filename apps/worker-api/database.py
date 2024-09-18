import hashlib
import re

from azure.data.tables import TableClient

REPOSITORY_URL = "https://github.com/Global-Hachathon-2024/msl-autogen-templates"

class Result:
    def __init__(self, url: str):
        url = rm_fragment(url)

        self.category = parse_get_category(url)
        self.url_hash = hashlib.sha256(url.encode()).hexdigest()
        self.in_progress = True
        self.is_valid = False
        self.stored_url = make_stored_url(url)

    def __str__(self) -> str:
        return f"{self.category} {self.url_hash} {self.in_progress} {self.is_valid} {self.stored_url}"

    def __repr__(self) -> str:
        return self.__str__()

    def __rm_fragment(self, url: str) -> str:
        return url.split('#')[0]
    
    def __parse_get_category(self, url: str):
        # input: "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal"
        # output: "storage"
        match = re.search(r'azure/([^/]+)/', url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Invalid URL: {url}")
    
    def __make_stored_url(self, url: str) -> str:
        # input: "https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli%2Cbrowser"
        # output: "https://github.com/Global-Hachathon-2024/msl-autogen-templates/azure-functions/create-first-function-cli-python+linux+bash+azure-cli+browser"
        match = re.search(r'azure/(.*)', url)
        if match:
            last_path = match.group(1)
            if '?tabs=' in last_path:
                repos_path, params = last_path.split('?tabs=')
                replaced_params = params.replace(',', '+')
                return f"{REPOSITORY_URL}/{repos_path}+{replaced_params}.json"
            else:
                repos_path = last_path
                return f"{REPOSITORY_URL}/{repos_path}.json"
        else:
            raise ValueError(f"Invalid URL: {url}")

    @classmethod
    def from_entity(cls, entity):
        return cls(
            category=entity['PartitionKey'],
            url_hash=entity['RowKey'],
            in_progress=entity['inProgress'],
            is_valid=entity['isValid'],
            stored_url=entity['storedUrl'],
        )

    def to_entity(self)->dict:
        return {
            u'PartitionKey': self.category,
            u'RowKey': self.url_hash,
            u'inProgress': self.in_progress,
            u'isValid': self.is_valid,
            u'storedUrl': self.stored_url,
        }

class DatabaseClient:
    _instance = None

    def __new__(cls, conn_str: str):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            cls._instance._initialize(conn_str)
        return cls._instance
    
    def _initialize(self, conn_str: str):
        self.table_client = TableClient.from_connection_string(conn_str, table_name="results")
    
    def get(self, url: str) -> Result:
        """
        Get the result from the database
        Args:
            url (str): URL to get the result
        Returns:
            Result: Result object
        """
        url = rm_fragment(url)
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        category= parse_get_category(url)
        entity = self.table_client.get_entity(partition_key=category, row_key=url_hash)
        return Result.from_entity(entity)

    def finish(self, url: str, is_valid: bool):
        """
        Change the status of result to finish
        Args:
            url (str): URL to finish
            is_valid (bool): Whether the generated template is valid or not
        """
        result = self.get(url)
        result.in_progress = False
        result.is_valid = is_valid
        entity = result.to_entity()
        self.table_client.update_entity(entity=entity, mode='replace')

def rm_fragment(url: str) -> str:
    """
    Remove the fragment from the URL
    Args:
        url (str): URL to remove the fragment like "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal#prerequisites"
    Returns:
        str: URL without the fragment like "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal"
    """
    return url.split('#')[0]

def parse_get_category(url: str) -> str:
    """
    Parse the category of the URL
    Args:
        url (str): URL to parse like "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal"
    Returns:
        str: category like "storage"
    """
    match = re.search(r'azure/([^/]+)/', url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid URL: {url}")

def make_stored_url(url: str) -> str:
    """
    Make the URL showing the repository and the path
    Args:
        url (str): URL to make the stored URL like "https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli%2Cbrowser"
    Returns:
        str: stored URL like ""https://github.com/Verify-Email-Tool-for-Outlook-new/msl-autogen-templates/azure-functions/create-first-function-cli-python+linux+bash+azure-cli+browser"
    """
    match = re.search(r'azure/(.*)', url)
    if match:
        last_path = match.group(1)
        if '?tabs=' in last_path:
            repos_path, params = last_path.split('?tabs=')
            replaced_params = params.replace(',', '+')
            return f"{REPOSITORY_URL}/{repos_path}+{replaced_params}.json"
        else:
            repos_path = last_path
            return f"{REPOSITORY_URL}/{repos_path}.json"
    else:
        raise ValueError(f"Invalid URL: {url}")