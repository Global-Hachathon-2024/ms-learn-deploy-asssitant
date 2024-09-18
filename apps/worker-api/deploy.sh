# !/bin/bash
zip -r worker-api.zip ./*
az webapp deploy -g hackathon2024 --name be3-appservice --src-path worker-api.zip