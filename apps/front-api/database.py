import datetime
import hashlib
import logging
import re

from azure.data.tables import TableClient, UpdateMode

REPOSITORY_URL = "https://github.com/Verify-Email-Tool-for-Outlook-new/msl-autogen-templates"

class Result:
    def __init__(self, url: str, exec_datetime: datetime.datetime):
        url = self.__rm_fragment(url)

        self.category = self.__parse_get_category(url)
        self.url_hash = hashlib.sha256(url.encode()).hexdigest()
        self.exec_datetime = exec_datetime
        self.isValid = False
        self.inProgress = True
        self.storedUrl = self.__make_stored_url(url)

    def __str__(self) -> str:
        return f"{self.category} {self.url_hash} {self.exec_datetime} {self.status} {self.stored_url}"

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
        # output: "https://github.com/Verify-Email-Tool-for-Outlook-new/msl-autogen-templates/azure-functions/create-first-function-cli-python+linux+bash+azure-cli+browser"
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
            exec_datetime=entity.metadata['timestamp'],
            isValid=entity['isValid'],
            inProgress = entity["inProgress"],
            stored_url=entity['storedUrl']
        )

    def to_entity(self):
        return {
            u'PartitionKey': self.category,
            u'RowKey': self.url_hash,
            u'Datetime': self.exec_datetime,
            u'isValid': self.isValid,
            u'inProgress': self.inProgress,
            u'storedUrl': self.storedUrl,
        }

class DatabaseClient:
    _instance = None

    def __new__(cls, conn_str: str):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            cls._instance._initialize(conn_str)
        return cls._instance
    
    def _initialize(self, conn_str: str):
        self.table_client = TableClient.from_connection_string(conn_str, table_name="testtable")
    
    def insert(self, result: Result):
        entity = result.to_entity()
        self.table_client.create_entity(entity=entity)
        logging.info(f"Inserted a new entity: {entity}")

    def get_result(self, partition_key: str, row_key: str):
        try:
            entity = self.table_client.get_entity(partition_key=partition_key, row_key=row_key)
            return entity
        except Exception as e:
            logging.error(f"Error retrieving entity: {e}")
            return None
    