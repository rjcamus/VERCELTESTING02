document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('reservation-date');
    const reserveButton = document.getElementById('reserve-button');
    const cartTableBody = document.querySelector('table tbody');

    // Set minimum date to today
    const today = new Date();
    const formattedToday = today.toISOString().split('T')[0];
    dateInput.setAttribute('min', formattedToday);

    // Function to check if a date is a weekend
    const isWeekend = (date) => {
        const day = date.getDay();
        return day === 0 || day === 6; // Sunday (0) and Saturday (6)
    };

    // Add an event listener to validate the date
    dateInput.addEventListener('change', (e) => {
        const selectedDate = new Date(e.target.value);
        if (selectedDate < today) {
            alert('Past dates and the current date are not allowed. Please select a valid date for your reservation.');
            e.target.value = ''; // Clear the invalid date
        } else if (isWeekend(selectedDate)) {
            alert('Weekends are not allowed. Please choose a weekday.');
            e.target.value = ''; // Clear the invalid date
        }
    });

    // Prevent manual input of invalid dates
    dateInput.addEventListener('keydown', (e) => {
        e.preventDefault(); // Disable manual entry
    });

    // Function to check if the tray is empty
    const checkTrayEmpty = () => {
        const rows = cartTableBody.querySelectorAll('tr');
        const isEmpty = rows.length === 1 && rows[0].textContent.trim() === 'Your cart is empty.';
        reserveButton.disabled = isEmpty;
    };

    // Check tray content initially
    checkTrayEmpty();

    // Update tray status dynamically (example: after a remove action)
    cartTableBody.addEventListener('DOMSubtreeModified', checkTrayEmpty);
});

// Function to disable page interactions
function disablePage() {
    // Prevent all mouse events
    document.addEventListener('mousedown', preventDefault, true);
    document.addEventListener('mouseup', preventDefault, true);
    document.addEventListener('click', preventDefault, true);
    document.addEventListener('contextmenu', preventDefault, true);

    // Prevent all keyboard events
    document.addEventListener('keydown', preventDefault, true);
    document.addEventListener('keyup', preventDefault, true);
}

// Function to enable page interactions
function enablePage() {
    // Restore all mouse events
    document.removeEventListener('mousedown', preventDefault, true);
    document.removeEventListener('mouseup', preventDefault, true);
    document.removeEventListener('click', preventDefault, true);
    document.removeEventListener('contextmenu', preventDefault, true);

    // Restore all keyboard events
    document.removeEventListener('keydown', preventDefault, true);
    document.removeEventListener('keyup', preventDefault, true);
}

// Helper function to prevent default behavior
function preventDefault(e) {
    e.preventDefault();
}

// Example of using these functions with page events
window.onload = enablePage; // Enable interactions when the page is fully loaded
window.onbeforeunload = disablePage; // Disable interactions when the page starts unloading