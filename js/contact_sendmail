function contactSendMail() {
    // 入力値を取得
    const detail = document.getElementById('detail').value;

    // バリデーション（簡単な入力チェック）
    if (!appName || !userId) {
        alert("全ての項目を入力してください。");
        return;
    }

    // メール本文を作成   
    const NL = "\r\n";  // 改行コードの変数定義

    let body  = "お問い合わせ内容" + NL + NL;
    body += "-----------------------------------------" + NL;
    body += detail + NL;
    body += "-----------------------------------------" + NL + NL;
    body += "※ 本メール送信後、本人確認のため、サポートより返信させていただく場合がございます。" + NL;

    // 宛先と件名（ここでは固定値）
    const to = "origia000@gmail.com"; // ★あなたのメールアドレスに変更してください
    const subject = "【ORIGIAWORKS】お問い合わせ";

    // mailtoリンクを生成して開く
    const mailtoLink = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    
    // ユーザーのメールクライアントを起動
    window.location.href = mailtoLink;
}
