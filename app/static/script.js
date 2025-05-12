document.querySelector('form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirm = document.getElementById('confirm_password').value;
    if (password !== confirm) {
        event.preventDefault();
        alert('Passwords do not match!');
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll("ul#elements li");
    const elementPositions = []; 

    elements.forEach(element => {
        let randomX, randomY, randomSize;
        let isOverlapping;

        do {
            // Generate random positions and size
            randomX = Math.random();
            randomY = Math.random();
            randomSize = Math.random();

            // Check for overlap with existing elements
            isOverlapping = elementPositions.some(pos => {
                const distanceX = Math.abs(pos.x - randomX);
                const distanceY = Math.abs(pos.y - randomY);
                return distanceX < 0.1 && distanceY < 0.1; // Adjust overlap threshold as needed
            });
        } while (isOverlapping);

        // Store the position to avoid future overlaps
        elementPositions.push({ x: randomX, y: randomY });

        // Apply the random values as CSS variables
        element.style.setProperty('--randomX', randomX);
        element.style.setProperty('--randomY', randomY);
        element.style.setProperty('--randomSize', randomSize);
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
    steamIDField.placeholder = 'Enter your Steam ID';

    // Change button to submit
    button.innerText = 'Link';
    button.setAttribute('type', 'submit');
    button.removeAttribute('onclick');  // Remove the onclick handler so it behaves like a submit button
}

function showLoadingPage() {
    document.getElementById('loading-overlay').style.display = 'flex'; // Show loading overlay
}

function openModal() {
    const modal = document.getElementById('shareModal');
    const resultsContainer = document.getElementById('searchResults');

    modal.style.display = 'flex'; // Show the modal
    resultsContainer.style.display = 'none'; // Hide the search results container
    resultsContainer.innerHTML = ''; // Clear any previous results
}

function openNameModal() {
    const modal = document.getElementById('nameModal');

    modal.style.display = 'flex'; // Show the modal
}

function closeModal() {
    const modals = ['nameModal', 'shareModal'];
    modals.forEach(id => {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'none';
        }
    });
}

window.onclick = function(event) {
    const modals = ['nameModal', 'shareModal'];
    modals.forEach(id => {
        const modal = document.getElementById(id);
        if (modal && event.target === modal) {
            modal.style.display = 'none';
        }
    });
};



document.getElementById('userSearch').addEventListener('input', function () {
    const query = this.value.trim();
    const resultsContainer = document.getElementById('searchResults');

    if (query.length < 2) {
        resultsContainer.innerHTML = ''; // Clear results
        resultsContainer.style.display = 'none'; // Hide the container
        return;
    }

    fetch(`/search_users?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = ''; // Clear previous results

            if (data.length === 0) {
                resultsContainer.innerHTML = '<p class="text-muted">No users found.</p>';
            } else {
                data.forEach(user => {
                    const userElement = document.createElement('div');
                    userElement.textContent = user.username;
                    userElement.className = 'search-result-item';
                    userElement.style.cursor = 'pointer';

                    // Onclick handler for selecting a user
                    userElement.onclick = () => {
                        
                        // Optionally, hide the search results after selection
                        resultsContainer.style.display = 'none';
                        
                        // Optionally, populate the input field with the selected username
                        document.getElementById('userSearch').value = user.username;
                    };

                    resultsContainer.appendChild(userElement);
                });
            }

            resultsContainer.style.display = 'block'; // Show the container
        })
        .catch(error => console.error('Error fetching search results:', error));
});

