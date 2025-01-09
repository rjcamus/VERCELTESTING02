function closeWindow() {
    if (window.opener) {
        window.close(); // Works if the page was opened by another window
    } else {
        window.history.back(); // Fallback to go back if the window wasn't opened by another window
    }
}

// JavaScript to toggle password visibility
const toggleOldPassword = document.getElementById("toggleOldPassword");
const oldPasswordInput = document.getElementById("oldPassword");
const toggleNewPassword = document.getElementById("toggleNewPassword");
const newPasswordInput = document.getElementById("newPassword");
const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
const confirmPasswordInput = document.getElementById("confirmNewPassword");

toggleOldPassword.addEventListener("click", () => {
    // Toggle the type attribute
    const type = oldPasswordInput.getAttribute("type") === "password" ? "text" : "password";
    oldPasswordInput.setAttribute("type", type);

    // Toggle the eye icon
    toggleOldPassword.classList.toggle("fa-eye");
    toggleOldPassword.classList.toggle("fa-eye-slash");
});

toggleNewPassword.addEventListener("click", () => {
    // Toggle the type attribute
    const type = newPasswordInput.getAttribute("type") === "password" ? "text" : "password";
    newPasswordInput.setAttribute("type", type);

    // Toggle the eye icon
    toggleNewPassword.classList.toggle("fa-eye");
    toggleNewPassword.classList.toggle("fa-eye-slash");
});

toggleConfirmPassword.addEventListener("click", () => {
    // Toggle the type attribute
    const type = confirmPasswordInput.getAttribute("type") === "password" ? "text" : "password";
    confirmPasswordInput.setAttribute("type", type);

    // Toggle the eye icon
    toggleConfirmPassword.classList.toggle("fa-eye");
    toggleConfirmPassword.classList.toggle("fa-eye-slash");
});