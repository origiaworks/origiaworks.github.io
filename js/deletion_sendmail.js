function deletionSendMail() {
    // 入力値を取得
    const appName = document.getElementById('app_name').value;
    const userId = document.getElementById('user_id').value;

    // バリデーション（簡単な入力チェック）
    if (!appName || !userId) {
        alert("全ての項目を入力してください。");
        return;
    }

    // メール本文を作成   
    const NL = "\r\n";  // 改行コードの変数定義

    let body  = "ゲームデータ削除を依頼します。" + NL + NL;
    body += "-----------------------------------------" + NL;
    body += "■ アプリ名: " + appName + NL;
    body += "■ ユーザーID: " + userId + NL;
    body += "-----------------------------------------" + NL + NL;
    body += "※ 本メールはデータ削除依頼専用です。" + NL;
    body += "※ 本メール送信後、本人確認のため、サポートより返信させていただく場合がございます。" + NL;

    // 宛先と件名（ここでは固定値）
    const to = "origia000@gmail.com"; // ★あなたのメールアドレスに変更してください
    const subject = "【ORIGIAWORKS】データ削除依頼";

    // mailtoリンクを生成して開く
    const mailtoLink = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    // ユーザーのメールクライアントを起動
    window.location.href = mailtoLink;
}
