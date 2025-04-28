document.querySelector('form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirm = document.getElementById('confirm_password').value;
    if (password !== confirm) {
        event.preventDefault();
        alert('Passwords do not match!');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('ul#elements li').forEach((el) => {
        el.style.setProperty('--random-x', Math.random());
        el.style.setProperty('--random-y', Math.random());
        el.style.setProperty('--random-size', Math.random());
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll("ul#elements li");

    elements.forEach(element => {
        // Generate random positions within the window dimensions
        const randomX = Math.random() * window.innerWidth;
        const randomY = Math.random() * window.innerHeight;

        // Apply the random positions to each element
        element.style.left = `${randomX}px`;
        element.style.top = `${randomY}px`;
    });
});

