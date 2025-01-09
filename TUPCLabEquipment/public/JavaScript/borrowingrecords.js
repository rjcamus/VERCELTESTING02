function filterRecords() {
    const searchInput = document.getElementById('search-bar').value.toLowerCase();
    const filter = document.getElementById('status-filter').value.toLowerCase();
    const rows = document.querySelectorAll('table tbody tr');

    rows.forEach(row => {
        const nameCell = row.cells[0]; // Name column
        const statusCell = row.cells[6]; // Status column

        if (nameCell && statusCell) {
            const name = nameCell.textContent.toLowerCase();
            const status = statusCell.textContent.toLowerCase();

            // Show the row if it matches both the search input and the selected filter
            row.style.display = (
                (name.includes(searchInput)) &&
                (filter === 'all' || status === filter)
            ) ? '' : 'none';
        }
    });
}

// Attach the combined filter function to the search and dropdown events
document.getElementById('search-bar').addEventListener('keyup', filterRecords);
document.getElementById('status-filter').addEventListener('change', filterRecords);


// Function to update the date input fields based on the selected status
function updateDateFields() {
    const status = document.getElementById('status-modal').value;
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const startDateLabel = document.querySelector('label[for="start-date"]');

    // Use month picker for all statuses
    startDateInput.setAttribute('type', 'month');
    endDateInput.setAttribute('type', 'month');
    startDateLabel.textContent = 'Select Month';
}

// Function to generate the report
function generateReport() {
    const month = document.getElementById('report-month').value;
    const status = document.getElementById('status-modal').value;

    // Validation
    if (!month) {
        alert('Please select a month.');
        return;
    }

    // Format the start and end dates based on the selected month
    const startDate = `${month}-01`; // First day of the selected month
    const endDate = new Date(new Date(month).getFullYear(), new Date(month).getMonth() + 1, 0)
        .toISOString()
        .split('T')[0]; // Last day of the selected month

    // Redirect to the generate-report endpoint with query parameters
    const reportUrl = `/generate-report/?start_date=${startDate}&end_date=${endDate}&status=${status}`;
    window.open(reportUrl, '_blank'); // Open the report in a new tab
}

// Initialize date fields based on the selected status when the page loads
document.addEventListener('DOMContentLoaded', () => {
    updateDateFields();
});
