import os
import re
from urllib.parse import unquote, urlparse


def convert_to_en_us_url(url):
    converted_url = re.sub(r'(https://learn\.microsoft\.com/)([^/]+/)', r'\1en-us/', url)
    return converted_url


def create_directory_from_url(url):
    print(url)
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query

    path_parts = path.strip("/").split("/")

    if path_parts[0] == "en-us":
        path_parts = path_parts[1:]
    if path_parts[0] == "azure":
        path_parts = path_parts[1:]

    if query:
        query = unquote(query)
        path_parts[-1] = f"{path_parts[-1]}_{query}"

    sanitized_parts = [re.sub(r'[<>:"/\\|?&]', '_', part) for part in path_parts]

    directory_path = os.path.join("deploy", *sanitized_parts)

    os.makedirs(directory_path, exist_ok=True)
    return directory_path
