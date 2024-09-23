import os
import re
from urllib.parse import unquote, urlparse

def save_files(directory_path, file_names, extracted_files):
    for filename in file_names:
        save_file(directory_path, filename, extracted_files)


def save_file(directory_path, filename, extracted_files):
    if filename in extracted_files:
        with open(os.path.join(directory_path, filename), "w") as f:
            f.write(extracted_files[filename])
        print(f"{filename} saved successfully.")
    else:
        print(f"{filename} not found in the output.")

def create_directory_from_url(url):
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