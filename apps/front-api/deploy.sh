# !/bin/bash
rm front-api.zip
zip -r front-api.zip ./*
az webapp deploy -g hackathon2024 --name msl-deploy-assistant-front-api --src-path front-api.zip