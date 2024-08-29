import datetime
import hashlib
import logging
import re

from azure.data.tables import TableClient

REPOSITORY_URL = "https://github.com/Verify-Email-Tool-for-Outlook-new/msl-autogen-templates"

class Result:
    def __init__(self, url: str, exec_datetime: datetime.datetime):
        url = self.__normalize_url(url)

        self.category = self.__parse_get_category(url)
        self.url_hash = hashlib.sha256(url.encode()).hexdigest()
        self.exec_datetime = exec_datetime
        self.status = False
        self.stored_url = self.__make_stored_url(url)

    def __str__(self):
        return f"{self.category} {self.url_hash} {self.exec_datetime} {self.status} {self.stored_url}"

    def __repr__(self):
        return self.__str__()

    def __normalize_url(self, url: str):
        return url.split('?')[0].split('#')[0]
    
    def __parse_get_category(self, url: str):
        # input: "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal"
        # output: "storage"
        match = re.search(r'azure/([^/]+)/', url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Invalid URL: {url}")
    
    def __make_stored_url(self, url: str):
        # input: "https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-portal"
        # output: "storage/blobs/storage-quickstart-blobs-portal.json"
        match = re.search(r'azure/(.*)', url)
        if match:
            sub_path = match.group(1)
            return f"{REPOSITORY_URL}/{sub_path}.json"
        else:
            raise ValueError(f"Invalid URL: {url}")

    @classmethod
    def from_entity(cls, entity):
        return cls(
            category=entity['PartitionKey'],
            url_hash=entity['RowKey'],
            exec_datetime=entity['datetime'],
            status=entity['status'],
            stored_url=entity['stored_url']
        )

    def to_entity(self):
        return {
            u'PartitionKey': self.category,
            u'RowKey': self.url_hash,
            u'datetime': self.exec_datetime,
            u'status': self.status,
            u'stored_url': self.stored_url,
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
    
    def upsert(self, result: Result):
        entity = result.to_entity()
        self.table_client.upsert_entity(entity=entity)
        logging.info(f"Inserted a new entity: {entity}")