import { useState, useEffect } from "react";
import "./App.css";

interface PollStatusResponse {
  status: "uninitialized" | "inProgress" | "completed" | "invalid";
  url: string;
}

interface GenerateResponse {
  status: string;
  url: string;
}

function App() {
  const [currentUrl, setCurrentUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [status, setStatus] = useState<string>("");
  const [storedUrl, setStoredUrl] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT;

  useEffect(() => {
    console.log(import.meta.env.MODE);
    // 現在のタブのURLを取得
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs: any[]) => {
      console.log(tabs);
      if (tabs[0].url && tabs[0].title) {
        const url = tabs[0].url;
        const title = tabs[0].title;
        setCurrentUrl(url);

        // タイトルに「Quickstart」または「クイックスタート」が含まれているかチェック
        if (
          title.includes("Quickstart") ||
          title.includes("クイックスタート")
        ) {
          // 対応しているサイトの場合、ステータスを取得
          pollStatus(url);
        } else {
          // 対応していないサイトの場合、エラーメッセージを表示
          setErrorMessage("このサイトはサポートされていません。");
        }
      } else {
        setErrorMessage("現在のタブのURLを取得できませんでした。");
      }
    });
  }, []);

  async function pollStatus(url: string) {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_ENDPOINT}/poll_status?url=${url}`);
      if (!response.ok) {
        throw new Error("HTTP error, status = " + response.status);
      }
      const data: PollStatusResponse = await response.json();
      console.log(data);
      setStatus(data.status);
      setStoredUrl(data.url);
    } catch (error) {
      console.log(`ステータス取得中にエラー: ${error}`);
      setErrorMessage("サーバーからステータスを取得できませんでした。");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleGenerate() {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_ENDPOINT}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: currentUrl }),
      });
      if (!response.ok) {
        throw new Error("HTTP error, status = " + response.status);
      }
      const data: GenerateResponse = await response.json();
      setStatus(data.status);
      setStoredUrl(data.url);
    } catch (error) {
      console.log(`テンプレート生成中にエラー: ${error}`);
      setErrorMessage("テンプレートの生成に失敗しました。");
    } finally {
      setIsLoading(false);
    }
  }

  function renderContent() {
    if (isLoading) {
      return <p>ロード中</p>;
    }

    if (errorMessage) {
      return <p>エラー：{errorMessage}</p>;
    }

    switch (status) {
      case "uninitialized":
        return (
          <div>
            <p>テンプレートはまだ生成されていません。</p>
            <button onClick={handleGenerate}>生成</button>
          </div>
        );
      case "inProgress":
        return (
          <div>
            <p>
              テンプレートを生成中です。他のユーザーが生成中の場合もあります。
            </p>
          </div>
        );
      case "completed":
        return (
          <div>
            <p>テンプレートの生成が完了しました。</p>
            <a href={storedUrl} target="_blank" rel="noopener noreferrer">
              テンプレートを見る
            </a>
          </div>
        );
      case "invalid":
        return (
          <div>
            <p>生成されたテンプレートは適切ではありません。</p>
            <button onClick={handleGenerate}>再生成</button>
            <p>手動で修正して貢献してみてください:</p>
            <a href={storedUrl} target="_blank" rel="noopener noreferrer">
              テンプレートを見る
            </a>
          </div>
        );
      default:
        return <p>ステータスを取得中です...</p>;
    }
  }

  return (
    <div>
      <h2>MS Learn Deploy Assistant</h2>
      {renderContent()}
    </div>
  );
}

export default App;
