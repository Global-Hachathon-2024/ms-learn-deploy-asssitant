Python バージョンの指定と依存関係のインストール
```sh
pyenv install 3.10
pyenv local 3.10
poetry install
```

ローカル実行時の注意点
* 環境変数 `AZURE_STORAGE_CONNECTION_STRING` は空文字列でOKで、代わりにlocal.settings.jsonの `AzureWebJobsStorage` に値を設定
https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-storage-queue-output?tabs=python-v2%2Cisolated-process%2Cnodejs-v4%2Cextensionv5&pivots=programming-language-python#connection-string
* VSCodeのWorkspaceで参照しているInterpreter（poetryで作った.venv）と自分が意図しているInterpreterが一致しているかを確認

```sh
# 関数アプリの作成
az functionapp create -g be3-practice --consumption-plan-location japaneast --runtime python --runtime-version 3.12 --functions-version 4 --name queue-trigger-funcapp --os-type linux --storage-account be3storage

# 関数アプリのデプロイ
func azure functionapp publish queue-trigger-funcapp

```