document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordToggleImg = document.getElementById('passwordToggleImg');

    passwordToggle.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            passwordToggleImg.src = "static/img/login_page/millenium-eye-48.png";
        } else {
            passwordInput.type = 'password';
            passwordToggleImg.src = "static/img/login_page/sleepy-eyes-48.png";
        }
    });
});
