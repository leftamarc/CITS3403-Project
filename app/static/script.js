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

function closeModal() {
    const modal = document.getElementById('shareModal');
    modal.style.display = 'none';
}

// Close the modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('shareModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
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

document.getElementById("saveCards").addEventListener("click", function () {
    const steamId = document.getElementById("saveCards").dataset.steamId; // Use a data attribute for steam_id
    const cards = [];

    document.querySelectorAll('.carousel-item .card').forEach(card => {
        cards.push(card.innerHTML);
    });

    if (!steamId || cards.length === 0) {
        alert("Error: Missing Steam ID or no cards to save.");
        return;
    }

    const combinedCards = cards.join('\n');

    fetch("/save_cards", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ steam_id: steamId, cards: combinedCards })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert("Saved successfully!");
        } else {
            alert("Error saving cards.");
        }
    })
    .catch(error => {
        console.error("Error during save:", error);
        alert("An unexpected error occurred.");
    });
});