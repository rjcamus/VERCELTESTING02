function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].classList.remove("active-content");
    }
    tablinks = document.getElementsByClassName("tab");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active-content");
    evt.currentTarget.classList.add("active");
}

function toggleUser(button) {
    const row = button.closest("tr");
    const action = button.textContent.trim();

    if (action === "Deactivate") {
        button.textContent = "Activate";
        button.classList.remove("btn-danger");
        button.classList.add("btn-success");
        row.style.textDecoration = "line-through";
    } else {
        button.textContent = "Deactivate";
        button.classList.remove("btn-success");
        button.classList.add("btn-danger");
        row.style.textDecoration = "none";
    }
}

function sortTable(columnIndex, tableId) {
    var table = document.getElementById(tableId);
    var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    switching = true;
    dir = "asc"; // Initial sort direction

    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[columnIndex];
            y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
            
            // Handle numerical columns
            const xValue = isNaN(x.innerHTML) ? x.innerHTML.toLowerCase() : parseFloat(x.innerHTML);
            const yValue = isNaN(y.innerHTML) ? y.innerHTML.toLowerCase() : parseFloat(y.innerHTML);

            if (dir == "asc") {
                if (xValue > yValue) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (xValue < yValue) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

function searchTable(inputId, tableId) {
    const searchInput = document.getElementById(inputId).value.toLowerCase().trim(); // Get search input, convert to lowercase and remove extra spaces
    const table = document.getElementById(tableId); // Get the table by ID
    const rows = table.getElementsByTagName('tr'); // Get all table rows
    
    for (let i = 1; i < rows.length; i++) { // Loop through all table rows, excluding the header row
        const cells = rows[i].getElementsByTagName('td'); // Get all cells in the row
        let rowMatch = false;

        for (let j = 0; j < cells.length; j++) { // Loop through cells in the row
            const cellText = cells[j].textContent.trim().toLowerCase(); // Get text content of the cell

            // Split cell text into words and check the first and second words (if they exist)
            const words = cellText.split(/\s+/); // Split by whitespace (space, tab, etc.)
            const firstWord = words[0];
            const secondWord = words[1] ? words[1] : ''; // Handle case where there's no second word

            // Check if the first or second word matches the search input
            if (firstWord.indexOf(searchInput) === 0 || secondWord.indexOf(searchInput) === 0) {
                rowMatch = true;
                break; // If a match is found in any word, no need to check other cells
            }
        }

        // Show or hide the row based on the match
        rows[i].style.display = rowMatch ? '' : 'none';
    }
}


function viewProof(button) {
    alert("Viewing proof for " + button.closest("tr").cells[0].innerText);
}

// Initialize event listeners for toggle buttons
document.querySelectorAll('.toggle-button').forEach(button => {
    button.addEventListener('click', function (event) {
        event.preventDefault();  // Prevent form submission (if needed)
        toggleUser(button);  // Call the toggle function
    });
});

