// Attach click event listeners to all dropdown buttons
document.querySelectorAll('.dropdown-button').forEach(button => {
    button.onclick = function(event) {
        // Removed event.stopPropagation() to allow document click handler to fire
        const popup = document.getElementById(button.getAttribute('data-target'));
        const buttonRect = event.target.getBoundingClientRect();

        // Close any other open dropdowns
        document.querySelectorAll('.dropdown-popup').forEach(otherPopup => {
            if (otherPopup !== popup) {
                otherPopup.classList.remove('show');
            }
        });

        // Calculate available space below the button
        const spaceBelow = window.innerHeight - buttonRect.bottom;
        const popupHeight = popup.offsetHeight;

        // If not enough space below, position the popup above the button
        if (spaceBelow < popupHeight) {
            popup.style.top = `${buttonRect.top + window.scrollY - popupHeight}px`;
        } else {
            popup.style.top = `${buttonRect.bottom + window.scrollY}px`;
        }

        // Set horizontal position and toggle visibility of the clicked dropdown
        popup.style.left = `${buttonRect.left + window.scrollX}px`;

        // Toggle visibility of the popup
        popup.classList.toggle('show');
    };
});

// Close dropdowns if clicking outside
document.addEventListener('click', function(event) {
    document.querySelectorAll('.dropdown-popup').forEach(popup => {
        // Ensure the click is outside of the dropdown button and popup
        if (!popup.contains(event.target) && !event.target.classList.contains('dropdown-button')) {
            popup.classList.remove('show');
        }
    });
});

// Close a specific dropdown by ID
function closePopup(popupId) {
    document.getElementById(popupId).classList.remove('show');
}

// Display details in a modal
function showDetails(name, items, quantity, dateClaim, requestId) {
    document.getElementById('detail-name').textContent = name; // Name
    document.getElementById('detail-items').textContent = items; // Items Borrowed
    document.getElementById('detail-quantity').textContent = quantity; // Quantity
    document.getElementById('detail-date-claim').textContent = dateClaim; // Date Claim

    const modal = new bootstrap.Modal(document.getElementById('detail-popup'));
    modal.show();

    document.getElementById('detail-popup').setAttribute('data-request-id', requestId);
}

// Handle approval or rejection of a request
let isRequestInProgress = false; // A flag to prevent multiple simultaneous requests
function handleRequest(action) {
    if (isRequestInProgress) return;

    isRequestInProgress = true;
    const requestId = document.getElementById('detail-popup').getAttribute('data-request-id');
    const acceptButton = document.getElementById('accept-button');
    const rejectButton = document.getElementById('reject-button');

    // Disable buttons and show processing state
    acceptButton.disabled = true;
    rejectButton.disabled = true;
    acceptButton.innerHTML = "Processing...";
    rejectButton.innerHTML = "Processing...";

    fetch('/labtech_homepage/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `request_id=${requestId}&action=${action}`
    })
    .then(response => {
        if (response.ok) {
            location.reload(); // Reload page on success
        } else {
            alert('Failed to update the request.');
        }
    })
    .finally(() => {
        // Reset buttons and flag after the process
        acceptButton.disabled = false;
        rejectButton.disabled = false;
        acceptButton.innerHTML = "Accept";
        rejectButton.innerHTML = "Reject";
        isRequestInProgress = false;
    });
}

// Retrieve a cookie by name
function getCookie(name) {
    const cookieArr = document.cookie.split(';').map(cookie => cookie.trim());
    const cookie = cookieArr.find(cookie => cookie.startsWith(name + '='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}

// Filter table rows based on search input and selected category
function filterTable() {
    const searchInput = document.getElementById('search-bar').value.trim().toLowerCase();
    const selectedCategory = document.getElementById('sort-dropdown').value.toLowerCase();
    const rows = document.querySelectorAll('#equipment-table tbody tr');

    rows.forEach(row => {
        const equipmentName = row.cells[0].textContent.trim().toLowerCase();
        const category = row.cells[2].textContent.toLowerCase();
        const matchesSearch = equipmentName.includes(searchInput);

        row.style.display = (
            (matchesSearch) && 
            (selectedCategory === "" || category === selectedCategory)
        ) ? '' : 'none';
    });
}

// Filter table by selected category
function filterByCategory() {
    const dropdown = document.getElementById('sort-dropdown');
    currentCategory = dropdown.value.toLowerCase();
    const rows = document.querySelectorAll('#equipment-table tbody tr');

    rows.forEach(row => {
        const category = row.cells[2].textContent.toLowerCase();
        row.style.display = (currentCategory === "" || category === currentCategory) ? '' : 'none';
    });

    document.getElementById('search-bar').value = ''; // Clear search input
}

// Preview selected image before upload
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('imagePreviewContainer');

    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = '<img src="' + e.target.result + '" style="max-width: 100%; max-height: 100%;" alt="Image Preview">';
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = 'No Image Selected';
            }
        });
    }
});

function previewImage(event) {
    var imagePreview = document.getElementById('imagePreview');
    var noImageSelected = document.getElementById('noImageSelected');
    var file = event.target.files[0];

    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            noImageSelected.style.display = 'none';
        }
        reader.readAsDataURL(file);
    } else {
        imagePreview.style.display = 'none';
        noImageSelected.style.display = 'block';
    }
    }

let currentCategory = ""; // Track the current selected category
