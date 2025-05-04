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
    const elementPositions = []; // store positions of elements

    elements.forEach(element => {
        let randomX, randomY;
        let isOverlapping;

        do {
            // Generate random positions within the window dimensions
            randomX = Math.random() * (window.innerWidth - element.offsetWidth);
            randomY = Math.random() * (window.innerHeight - element.offsetHeight);

            // Check for overlap with existing elements
            isOverlapping = elementPositions.some(pos => {
                const distanceX = Math.abs(pos.x - randomX);
                const distanceY = Math.abs(pos.y - randomY);
                return distanceX < element.offsetWidth && distanceY < element.offsetHeight;
            });
        } while (isOverlapping);

        // Store the position to avoid future overlaps
        elementPositions.push({ x: randomX, y: randomY });

        // Apply the random positions to each element
        element.style.position = "absolute"; // Ensure position is absolute
        element.style.left = `${randomX}px`;
        element.style.top = `${randomY}px`;
    });
});

document.addEventListener("DOMContentLoaded", () => {
    let formSubmitted = false;

    const form = document.querySelector("form");
    const pathname = window.location.pathname;
    const monitoredPages = ["/login", "/register"];

    if (form && monitoredPages.includes(pathname)) {
        // Track submission via buttons only
        const submitButtons = form.querySelectorAll("button[type='submit'], input[type='submit']");

        submitButtons.forEach(button => {
            button.addEventListener("click", () => {
                formSubmitted = true;
            });
        });

        // Fallback: If form is submitted (e.g., via Enter key), mark as submitted
        form.addEventListener("submit", () => {
            formSubmitted = true;
        });

        window.addEventListener("beforeunload", function (e) {
            if (!formSubmitted) {
                e.preventDefault();            }
        });
    }
});

function resetToLink() {
    const steamIDField = document.getElementById('steam_id');
    const button = document.getElementById('editToggleButton');

    // Enable the field and clear the value
    steamIDField.disabled = false;
    steamIDField.value = '';
    steamIDField.placeholder = 'Enter your Steam ID';

    // Change button to submit
    button.innerText = 'Link';
    button.setAttribute('type', 'submit');
    button.removeAttribute('onclick');  // remove JS handler so it behaves like a submit button
}

function showLoadingPage() {
    document.getElementById('loading-overlay').style.display = 'flex'; // Show loading overlay
}

//function hideLoadingPage() {
//    document.getElementById('loading-overlay').style.display = 'none'; // Hide loading overlay
//}
