        // Function to automatically capitalize each word in the input
        function capitalizeWords(input) {
            input.value = input.value
                .toLowerCase() // Convert all characters to lowercase first
                .replace(/\b\w/g, char => char.toUpperCase()); // Capitalize the first letter of each word
        }

        function restrictNumbers(input) {
            input.value = input.value.replace(/[0-9]/g, ''); // Remove any numbers
        }

        // Function to format the Student ID field
        function formatStudentId(input) {
            const value = input.value.toUpperCase().replace(/[^A-Z0-9-]/g, ''); // Allow only letters, digits, and hyphens
            if (!value.startsWith("TUPC-")) {
                input.value = "TUPC-"; // Ensure it starts with "TUPC-"
            } else {
                let numbers = value.slice(5).replace(/-/g, ''); // Remove "TUPC-" and existing hyphens
                if (numbers.length > 2) {
                    numbers = numbers.slice(0, 2) + '-' + numbers.slice(2); // Add hyphen after 2 digits
                }
                input.value = "TUPC-" + numbers;
            }
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
