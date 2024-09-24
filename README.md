# ms-learn-deploy-asssitant

ディレクトリ構成（必要に応じて追加/変更して下さい）
- apps: 各種アプリケーションのコード
  - web-extension: ブラウザ拡張機能のコード
  - front-api: ブラウザ拡張機能から呼び出されるAPIのコード
  - worker-api: テンプレート生成依頼を受け付けるAPIのコード
- infra: インフラ構築用のコード（ARM Template or Bicep）

※front-api, worker-apiは上手く共通の依存関係と固有の依存関係を切り分けて管理したいけど検討中。
