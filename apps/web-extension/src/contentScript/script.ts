// メッセージを受信するリスナーを設定
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "CHECK_QUICKSTART_PAGE") {
    const contentDiv = document.querySelector("div.content");
    let isQuickstartPage = false;

    if (contentDiv) {
      const h1Element = contentDiv.querySelector("h1");
      if (h1Element) {
        const h1Text = h1Element.textContent || "";
        if (
          h1Text.includes("Quickstart") ||
          h1Text.includes("クイックスタート") ||
          h1Text.includes("クイック スタート")
        ) {
          isQuickstartPage = true;
        }
      }
    }

    // 結果を返信
    sendResponse({ isQuickstartPage });
  }
});
