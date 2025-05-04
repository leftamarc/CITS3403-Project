
document.querySelector('form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirm = document.getElementById('confirm_password').value;
    if (password !== confirm) {
        event.preventDefault();
        alert('Passwords do not match!');
    }
});

document.addEventListener("DOMContentLoaded", () => {
    let formSubmitted = false;

    const form = document.querySelector("form");
    const pathname = window.location.pathname;
    const monitoredPages = ["/login", "/register"];

    if (form && monitoredPages.includes(pathname)) {
        form.addEventListener("submit", () => {
            formSubmitted = true;
        });

        window.addEventListener("beforeunload", function (e) {
            if (!formSubmitted) {
                e.preventDefault();
                e.returnValue = ''; // Required for Chrome to show alert
            }
        });
    }
});




