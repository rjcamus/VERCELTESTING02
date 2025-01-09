// JavaScript to toggle profile links
function toggleProfileLinks() {
    const profileLinks = document.getElementById("profileLinks");
    const profile = document.querySelector('.profile');

    // Toggle the display of the profile links
    if (profileLinks.style.display === "block") {
        profileLinks.style.display = "none";
    } else {
        profileLinks.style.display = "block";
    }

    // Add hover state styles when profile is open
    profile.classList.toggle('hover-active', profileLinks.style.display === 'block');
}

// Optional: Close dropdown if clicked outside of profile
window.onclick = function(event) {
    if (!event.target.matches('.profile') && !event.target.matches('.profile img')) {
        var profileLinks = document.getElementById("profileLinks");
        if (profileLinks.style.display === 'block') {
            profileLinks.style.display = 'none';
        }
    }
}

// Adjust the header and navbar size when the burger menu is toggled
const navbarCollapse = document.getElementById("navbarNav");
const header = document.getElementById("home"); // Adjusted ID to match your HTML header section

navbarCollapse.addEventListener('show.bs.collapse', function () {
    // When the burger menu is opened, adjust the navbar height
    header.style.height = "auto"; // Adjust as needed
    header.classList.add("expanded");
});

navbarCollapse.addEventListener('hide.bs.collapse', function () {
    // When the burger menu is closed, reset the navbar height
    header.style.height = "unset"; // Reset to default height
    header.classList.remove("expanded");
});
