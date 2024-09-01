Python バージョンの指定と依存関係のインストール
```sh
pyenv install 3.10
pyenv local 3.10
poetry install
```

```sh
# 関数アプリの作成
az functionapp create -g be3-practice --consumption-plan-location japaneast --runtime python --runtime-version 3.12 --functions-version 4 --name queue-trigger-funcapp --os-type linux --storage-account be3storage

# 関数アプリのデプロイ
func azure functionapp publish queue-trigger-funcapp

```