import hashlib

url="https://learn.microsoft.com/en-us/azure/app-service/quickstart-nodejs?tabs=windows&pivots=development-environment-vscode"
url_hash = hashlib.sha256(url.encode()).hexdigest()
print(url_hash)