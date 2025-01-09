    // Open modal by ID
    function openModal(modalId) {
        document.getElementById(modalId).style.display = "block";
    }

    // Close modal by ID
    function closeModal(modalId) {
        document.getElementById(modalId).style.display = "none";
    }

    // Submit forgot password form using AJAX
    function submitForgotPasswordForm(event) {
        event.preventDefault(); // Prevent default form submission

        // Get the "SEND EMAIL" button and spinner container
        var sendEmailBtn = document.getElementById("sendEmailBtn");
        var spinnerContainer = document.getElementById("spinner-container");
        var overlay = document.getElementById("loading-overlay");

        // Disable the button, show the loading spinner and overlay
        sendEmailBtn.disabled = true;
        spinnerContainer.style.display = "flex"; // Show spinner and text
        overlay.style.display = "block"; // Show overlay

        // Get email value
        var email = document.getElementById("forgot-email").value;

        // Send AJAX request to send OTP
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "{% url 'forgot_password' %}", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status == "success") {
                    // Open OTP modal on success
                    closeModal('forgotPasswordModal');
                    openModal('otpModal');
                } else {
                    // Handle error response, show alert or message
                    alert(response.message);
                }
            } else if (xhr.readyState == 4) {
                // Handle error response
                alert("Error: " + xhr.responseText);
            }

            // Hide loading spinner, hide overlay, and re-enable the button after the request
            spinnerContainer.style.display = "none"; // Hide spinner and text
            overlay.style.display = "none"; // Hide overlay
            sendEmailBtn.disabled = false; // Re-enable the button
        };
        xhr.send("email=" + encodeURIComponent(email));
    }

    // Submit OTP form using AJAX and validate OTP
    function submitOtpForm(event) {
        event.preventDefault(); // Prevent default form submission

        // Get email and OTP code values
        var email = document.getElementById("forgot-email").value;
        var otp_code = document.getElementById("otp-code").value;

        // Send AJAX request to validate OTP
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "{% url 'forgot_passwordotp' %}", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status == "success") {
                    // Open Change Password modal on OTP success
                    closeModal('otpModal');
                    openModal('changePasswordModal');
                } else {
                    // Handle invalid OTP
                    alert(response.message);
                }
            } else if (xhr.readyState == 4) {
                // Handle error response
                alert("Error: " + xhr.responseText);
            }
        };
        xhr.send("email=" + encodeURIComponent(email) + "&otp_code=" + encodeURIComponent(otp_code));
    }

    // Submit Change Password form using AJAX
    function submitChangePasswordForm(event) {
        event.preventDefault(); // Prevent default form submission

        // Get email, new password, and confirm password values
        var email = document.getElementById("forgot-email").value;
        var newPassword = document.getElementById("newPassword").value;
        var confirmPassword = document.getElementById("confirmPassword").value;

        // Check if passwords match
        if (newPassword !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        // Send AJAX request to reset the password
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "{% url 'forgot_password_reset' %}", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.setRequestHeader("X-CSRFToken", document.querySelector('[name=csrfmiddlewaretoken]').value);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status == "success") {
                    // Close the Change Password modal and show success message
                    closeModal('changePasswordModal');
                    alert(response.message); // Optionally show a success message
                } else {
                    // Handle error response
                    alert(response.message);
                }
            } else if (xhr.readyState == 4) {
                // Handle error response
                alert("Error: " + xhr.responseText);
            }
        };
        xhr.send("email=" + encodeURIComponent(email) + "&newPassword=" + encodeURIComponent(newPassword) + "&confirmPassword=" + encodeURIComponent(confirmPassword));
    }

    // JavaScript to toggle password visibility
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");

    togglePassword.addEventListener("click", () => {
        // Toggle the type attribute
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);

        // Toggle the eye icon
        togglePassword.classList.toggle("fa-eye");
        togglePassword.classList.toggle("fa-eye-slash");
    });

    function togglePasswordCheckbox() {
        const newPasswordField = document.getElementById("newPassword");
        const confirmPasswordField = document.getElementById("confirmPassword");
        const showPasswordCheckbox = document.getElementById("showPassword");

        if (showPasswordCheckbox.checked) {
            newPasswordField.type = "text";
            confirmPasswordField.type = "text";
        } else {
            newPasswordField.type = "password";
            confirmPasswordField.type = "password";
        }
    }