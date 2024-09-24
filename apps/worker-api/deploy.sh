# !/bin/bash
rm worker-api.zip
zip -r worker-api.zip ./* -x ".venv/*" -x "deploy.sh" -x "__pycache__/*"
az webapp deploy -g hackathon2024 --name be3-appservice --src-path worker-api.zip