// EmailJS 初期化
emailjs.init({
    publicKey: "lEActPSPkZVjo0og8"
});

// フォーム送信処理
document.getElementById('deletion-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const formMessage = document.getElementById('form-message');

    submitBtn.disabled = true;
    submitBtn.textContent = "送信中...";

    emailjs.sendForm("service_xeoggyw", "template_hhzdo2m", this)
        .then(() => {
            formMessage.style.color = "green";
            formMessage.textContent = "送信が完了しました。";
            this.reset();
        })
        .catch(() => {
            formMessage.style.color = "red";
            formMessage.textContent = "送信に失敗しました。時間をおいて再度お試しください。";
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = "送信する";
        });
});
