# !/bin/bash
rm front-api.zip
zip -r front-api.zip ./* -x ".venv/*" -x "deploy.sh" -x "__pycache__/*"
az webapp deploy -g hackathon2024 --name msl-deploy-assistant-front-api --src-path front-api.zip