function sendMail() {
    // 入力値を取得
    const appName = document.getElementById('app_name').value;
    const userId = document.getElementById('user_id').value;

    // バリデーション（簡単な入力チェック）
    if (!appName || !userId) {
        alert("全ての項目を入力してください。");
        return;
    }

    // メール本文を作成
    // 改行は %0A （URLエンコードされた改行コード）を使用
    let body  += "ゲームデータ削除を依頼します。%0A%0A";
    body += "-----------------------------------------%0A";
    body += "■ アプリ名: " + appName + "%0A";
    body += "■ ユーザーID: " + userId + "%0A";
    body += "-----------------------------------------%0A%0A";
    body += "※ 本メールはデータ削除依頼専用です。%0A";
    body += "※ 本メール送信後、本人確認のため、サポートより返信させていただく場合がございます。%0A";

    // 宛先と件名（ここでは固定値）
    const to = "origia000@gmail.com"; // ★あなたのメールアドレスに変更してください
    const subject = "【ORIGIAWORKS】データ削除依頼";

    // mailtoリンクを生成して開く
    const mailtoLink = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    // ユーザーのメールクライアントを起動
    window.location.href = mailtoLink;
}
