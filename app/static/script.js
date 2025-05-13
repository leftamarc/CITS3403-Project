document.querySelector('form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirm = document.getElementById('confirm_password').value;
    if (password !== confirm) {
        event.preventDefault();
        alert('Passwords do not match!');
    }
});

document.addEventListener("DOMContentLoaded", () => {
    positionAnimatedElements();
});

function positionAnimatedElements() {
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
                return distanceX < 0.1 && distanceY < 0.1;
            });
        } while (isOverlapping);

        // Store the position to avoid future overlaps
        elementPositions.push({ x: randomX, y: randomY });

        // Apply the random values as CSS variables
        element.style.setProperty('--randomX', randomX);
        element.style.setProperty('--randomY', randomY);
        element.style.setProperty('--randomSize', randomSize);
    });
};

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

/* SEARCH FOR USERS WHEN SHARING (VIEW)*/

document.getElementById('search_username').addEventListener('input', function () {
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
                        document.getElementById('search_username').value = user.username;
                    };

                    resultsContainer.appendChild(userElement);
                });
            }

            resultsContainer.style.display = 'block'; // Show the container
        })
        .catch(error => console.error('Error fetching search results:', error));
});

/* TOGGLE BETWEEN SAVED AND SHARED COLLECTIONS */

function showSaved() {
    document.getElementById('savedCollectionsBox').style.display = 'block';
    document.getElementById('sharedCollectionsBox').style.display = 'none';
    document.getElementById('toggleSaved').classList.add('btn-primary');
    document.getElementById('toggleSaved').classList.remove('btn-secondary');
    document.getElementById('toggleShared').classList.add('btn-secondary');
    document.getElementById('toggleShared').classList.remove('btn-primary');
}

function showShared() {
    document.getElementById('savedCollectionsBox').style.display = 'none';
    document.getElementById('sharedCollectionsBox').style.display = 'block';
    document.getElementById('toggleShared').classList.add('btn-primary');
    document.getElementById('toggleShared').classList.remove('btn-secondary');
    document.getElementById('toggleSaved').classList.add('btn-secondary');
    document.getElementById('toggleSaved').classList.remove('btn-primary');
}

/* SHARE MODAL ON PAGE LOAD AFTER CLICKING SHARE IN PROFILE */

document.addEventListener("DOMContentLoaded", () => {
    // Check if the URL contains the "share=true" query parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('share') === 'true') {
        openModal(); // Open the share modal
    }
});

/* FLASH MESSAGES - AUTO DISMISS */

window.addEventListener('DOMContentLoaded', () => {
    const alert = document.getElementById('autoDismissAlert');
    if (alert) {
      setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      }, 3000); // 3000ms = 3 seconds
    }
  });

/* MODALS */

function openModal(modalId) {
    const modal = document.getElementById(modalId); // Select the modal by its ID
    if (modal) {
        modal.style.display = 'flex'; // Show the modal
        if (modalId === 'share_modal') {
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.style.display = 'none'; // Hide the search results container
            resultsContainer.innerHTML = ''; // Clear any previous results
        }
    } else {
        console.error("Modal not found");
    }
}

function closeModal() {
    const modals = document.querySelectorAll('.modal'); // Select all elements with the class 'modal'
    modals.forEach(modal => {
        modal.style.display = 'none'; // Hide each modal
    });
}

window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal'); // Select all elements with the 'modal' class
    modals.forEach(modal => {
        if (modal && event.target === modal) { // Check if the clicked target is the modal itself
            modal.style.display = 'none'; // Hide the modal
        }
    });
};
