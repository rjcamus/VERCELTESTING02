function capitalizeWords(input) {
    input.value = input.value.replace(/\b\w/g, char => char.toUpperCase());
}
function restrictNumbers(input) {
    input.value = input.value.replace(/[0-9]/g, ''); // Remove any numbers
}

// JavaScript to toggle password visibility
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");
const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
const confirmPasswordInput = document.getElementById("confirm-password");

togglePassword.addEventListener("click", () => {
    // Toggle the type attribute
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);

    // Toggle the eye icon
    togglePassword.classList.toggle("fa-eye");
    togglePassword.classList.toggle("fa-eye-slash");
});

toggleConfirmPassword.addEventListener("click", () => {
    // Toggle the type attribute
    const type = confirmPasswordInput.getAttribute("type") === "password" ? "text" : "password";
    confirmPasswordInput.setAttribute("type", type);

    // Toggle the eye icon
    toggleConfirmPassword.classList.toggle("fa-eye");
    toggleConfirmPassword.classList.toggle("fa-eye-slash");
});