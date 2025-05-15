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

    const form = document.querySelector("#login-form");
    const pathname = window.location.pathname;
    const monitoredPages = ["/login", "/register"];

    if (form && monitoredPages.includes(pathname)) {
        // Use 'mousedown' to catch user intent early
        const submitButtons = form.querySelectorAll("button[type='submit'], input[type='submit']");
        submitButtons.forEach(button => {
            button.addEventListener("mousedown", () => {
                formSubmitted = true;
            });
        });

        // Also mark as submitted if the form is submitted (e.g. via Enter key)
        form.addEventListener("submit", () => {
            formSubmitted = true;
        });

        // Warn the user if they try to leave without submitting
        window.addEventListener("beforeunload", function (e) {
            if (!formSubmitted) {
                e.preventDefault();
                e.returnValue = ""; 
            }
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

document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.getElementById('search_username');
    const resultsContainer = document.getElementById('searchResults');

    inputField.addEventListener('focus', () => {
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
    });

    inputField.addEventListener('input', function () {
        const query = this.value.trim();

        if (query === '') {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
            return; 
        }

        fetch(`/search_users?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = '';

                if (data.length === 0) {
                    resultsContainer.innerHTML = '<p class="text-muted m-2">No users found.</p>';
                } else {
                    data.forEach(user => {
                        const userElement = document.createElement('div');
                        userElement.textContent = user.username;
                        userElement.className = 'search-result-item';
                        userElement.style.cursor = 'pointer';
                        userElement.style.padding = '6px 10px';

                        userElement.onclick = () => {
                            resultsContainer.style.display = 'none';
                            inputField.value = user.username;
                        };

                        resultsContainer.appendChild(userElement);
                    });
                }

                resultsContainer.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                resultsContainer.style.display = 'none';
            });
    });

    document.getElementById('share_modal').addEventListener('show.bs.modal', function () {
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
    });
});

/* TOGGLE BETWEEN SAVED AND SHARED COLLECTIONS */

function showSaved() {
    document.getElementById('savedCollectionsBox').style.display = 'block';
    document.getElementById('sharedCollectionsBox').style.display = 'none';
    document.getElementById('toggleSaved').classList.add('btn-blue');
    document.getElementById('toggleSaved').classList.remove('btn-secondary');
    document.getElementById('toggleShared').classList.add('btn-secondary');
    document.getElementById('toggleShared').classList.remove('btn-blue');
}

function showShared() {
    document.getElementById('savedCollectionsBox').style.display = 'none';
    document.getElementById('sharedCollectionsBox').style.display = 'block';
    document.getElementById('toggleShared').classList.add('btn-blue');
    document.getElementById('toggleShared').classList.remove('btn-secondary');
    document.getElementById('toggleSaved').classList.add('btn-secondary');
    document.getElementById('toggleSaved').classList.remove('btn-blue');
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
