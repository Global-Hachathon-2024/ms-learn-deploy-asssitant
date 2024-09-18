import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../.env")


def deploy_bicep(directory_path):
    command = [
        "az",
        "deployment",
        "group",
        "create",
        "--resource-group",
        os.environ.get("RESOURCE_GROUP"),
        "--template-file",
        os.path.join(directory_path, os.environ.get("BICEP_FILE")),
        "--parameters",
        os.path.join(directory_path, os.environ.get("PARAMETERS_FILE")),
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def convert_bicep_to_json(directory_path):
    command = [
        "az",
        "bicep",
        "build",
        "--file",
        os.path.join(directory_path, os.environ.get("BICEP_FILE")),
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
