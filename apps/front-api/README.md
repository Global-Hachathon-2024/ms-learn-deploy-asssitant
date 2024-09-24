Python バージョンの指定と依存関係のインストール
```sh
pyenv install 3.12
pyenv local 3.12.3
poetry install
```

サーバーの起動
```sh
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```