document.querySelectorAll('.dropdown-button').forEach(button => {
    button.onclick = function(event) {
        event.stopPropagation();
        const popup = document.getElementById(button.getAttribute('data-target'));
        const buttonRect = event.target.getBoundingClientRect();

        // Close any other open dropdowns
        document.querySelectorAll('.dropdown-popup').forEach(otherPopup => {
            if (otherPopup !== popup) {
                otherPopup.classList.remove('show');
            }
        });

        // Set position and toggle visibility of the clicked dropdown
        popup.style.top = `${buttonRect.bottom + window.scrollY}px`; 
        popup.style.left = `${buttonRect.left + window.scrollX}px`;
        popup.classList.toggle('show');
    };
});

// Close dropdowns if clicking outside
document.addEventListener('click', function(event) {
    document.querySelectorAll('.dropdown-popup').forEach(popup => {
        if (!popup.contains(event.target) && !event.target.classList.contains('dropdown-button')) {
            popup.classList.remove('show');
        }
    });
});

// Close specific dropdown
function closePopup(popupId) {
    document.getElementById(popupId).classList.remove('show');
}

function showDetails(name, items, quantity, dateClaim, requestId) {
    document.getElementById('detail-name').textContent = name; // Name
    document.getElementById('detail-items').textContent = items; // Items Borrowed
    document.getElementById('detail-quantity').textContent = quantity; // Quantity
    document.getElementById('detail-date-claim').textContent = dateClaim; // Date Claim

    var modal = new bootstrap.Modal(document.getElementById('detail-popup'));
    modal.show();

    document.getElementById('detail-popup').setAttribute('data-request-id', requestId);
}



function handleRequest(action) {
    const requestId = document.getElementById('detail-popup').getAttribute('data-request-id');
    fetch('/labtech_homepage/', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')  
        },
        body: `request_id=${requestId}&action=${action}`
    })
    .then(response => response.ok ? location.reload() : alert('Failed to update the request.'));
}

function getCookie(name) {
    const cookieArr = document.cookie.split(';').map(cookie => cookie.trim());
    const cookie = cookieArr.find(cookie => cookie.startsWith(name + '='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}

document.querySelectorAll('.dropdown-button').forEach(button => {
    button.onclick = function(event) {
        event.stopPropagation();
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

        // If there's not enough space below, position the popup above the button
        if (spaceBelow < popupHeight) {
            popup.style.top = `${buttonRect.top + window.scrollY - popupHeight}px`; // Position above
        } else {
            popup.style.top = `${buttonRect.bottom + window.scrollY}px`; // Position below
        }

        // Set horizontal position and toggle visibility of the clicked dropdown
        popup.style.left = `${buttonRect.left + window.scrollX}px`;
        popup.classList.toggle('show');
    };
});

// Close dropdowns if clicking outside
document.addEventListener('click', function(event) {
    document.querySelectorAll('.dropdown-popup').forEach(popup => {
        if (!popup.contains(event.target) && !event.target.classList.contains('dropdown-button')) {
            popup.classList.remove('show');
        }
    });
});

function filterTable() {
    const searchInput = document.getElementById('search-bar').value.toLowerCase();
    const selectedCategory = document.getElementById('sort-dropdown').value.toLowerCase();
    const rows = document.querySelectorAll('#equipment-table tbody tr');

    rows.forEach(row => {
        const equipmentName = row.cells[0].textContent.toLowerCase();
        const category = row.cells[2].textContent.toLowerCase();

        // Display row only if it matches both the search input and the selected category (if any)
        row.style.display = (
            (equipmentName.includes(searchInput)) && 
            (selectedCategory === "" || category === selectedCategory)
        ) ? '' : 'none';
    });
}

function filterByCategory() {
    const dropdown = document.getElementById('sort-dropdown');
    currentCategory = dropdown.value.toLowerCase();
    const rows = document.querySelectorAll('#equipment-table tbody tr');

    rows.forEach(row => {
        const category = row.cells[2].textContent.toLowerCase();
        row.style.display = (currentCategory === "" || category === currentCategory) ? '' : 'none';
    });

    // Clear the search input whenever a new category is selected
    document.getElementById('search-bar').value = '';
}

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

let currentCategory = "";

function filterRecords() {
    const searchInput = document.getElementById('search-bar').value.toLowerCase();
    const filter = document.getElementById('status-filter').value.toLowerCase();
    const rows = document.querySelectorAll('table tbody tr');

    // Handle filtering for 'All' first 30 recent records
    if (filter === 'all') {
        // Only show the first 30 records for the 'all' filter
        const visibleRows = Array.from(rows).slice(0, 30);
        visibleRows.forEach(row => {
            const nameCell = row.cells[0]; // Name column
            const statusCell = row.cells[6]; // Status column

            if (nameCell && statusCell) {
                const name = nameCell.textContent.toLowerCase();
                const status = statusCell.textContent.toLowerCase();

                // Show the row if it matches the search input
                row.style.display = (name.includes(searchInput)) ? '' : 'none';
            }
        });

        // Hide the rest of the rows
        rows.forEach(row => {
            if (!visibleRows.includes(row)) {
                row.style.display = 'none';
            }
        });
    } else {
        // Show all records for other status options
        rows.forEach(row => {
            const nameCell = row.cells[0]; // Name column
            const statusCell = row.cells[6]; // Status column

            if (nameCell && statusCell) {
                const name = nameCell.textContent.toLowerCase();
                const status = statusCell.textContent.toLowerCase();

                // Show the row if it matches both the search input and the selected filter
                row.style.display = (
                    (name.includes(searchInput)) &&
                    (status === filter)
                ) ? '' : 'none';
            }
        });
    }
}

// Attach the combined filter function to the search and dropdown events
document.getElementById('search-bar').addEventListener('keyup', filterRecords);
document.getElementById('status-filter').addEventListener('change', filterRecords);