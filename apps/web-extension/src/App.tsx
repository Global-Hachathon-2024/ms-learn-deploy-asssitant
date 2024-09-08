import { useState } from "react";
// import reactLogo from "./assets/react.svg";
// import viteLogo from "/vite.svg";
import "./App.css";

type Status = "uninitialized" | "inProgress" | "completed";

function App() {
  const [generationStatus, setGenerationStatus] =
    useState<Status>("uninitialized");

  const startProcess = () => {
    // ステータスを生成中に変更
    setGenerationStatus("inProgress");

    // シミュレーションとして、3秒後に生成後に変更
    setTimeout(() => {
      setGenerationStatus("completed");
    }, 3000);
  };

  return (
    <>
      {(() => {
        switch (generationStatus) {
          case "uninitialized":
            return (
              <div>
                <button onClick={startProcess}>Start</button>
              </div>
            );
          case "inProgress":
            return <div>Generation in progress...</div>;
          case "completed":
            return <div>Generation completed!</div>;
        }
      })()}
    </>
  );
}

export default App;
