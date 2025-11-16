
        function sendMail() {
            // 入力値を取得
            const appName = document.getElementById('app_name').value;
            const userId = document.getElementById('user_id').value;
            const emailAddr = document.getElementById('email_addr').value;

            // バリデーション（簡単な入力チェック）
            if (!appName || !userId || !emailAddr) {
                alert("全ての項目を入力してください。");
                return;
            }

            // メール本文を作成
            // 改行は %0A （URLエンコードされた改行コード）を使用
            let body = "以下の情報でお問い合わせがありました。%0A%0A";
            body += "アプリ名: " + appName + "%0A";
            body += "ユーザーID: " + userId + "%0A";
            body += "メールアドレス: " + emailAddr + "%0A";

            // 宛先と件名（ここでは固定値）
            const to = "origia000@gmail.com"; // ★あなたのメールアドレスに変更してください
            const subject = "アプリからの問い合わせ";

            // mailtoリンクを生成して開く
            const mailtoLink = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
            
            // ユーザーのメールクライアントを起動
            window.location.href = mailtoLink;
        }
