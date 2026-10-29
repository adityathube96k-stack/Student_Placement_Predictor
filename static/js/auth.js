document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;

        const message =
            document.getElementById("loginMessage");

        const loginButton =
            document.getElementById("loginButton");


        // Clear previous message
        message.style.display = "none";
        message.textContent = "";


        // Basic validation
        if (!email || !password) {

            showMessage(
                "Please enter email and password.",
                "error"
            );

            return;
        }


        // Disable button
        loginButton.disabled = true;
        loginButton.textContent = "Logging in...";


        try {

            const response = await fetch(
                "/api/auth/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


            const data = await response.json();


            if (response.ok && data.success) {

                showMessage(
                    "Login successful. Redirecting...",
                    "success"
                );

                setTimeout(() => {

                    window.location.href = "/dashboard";

                }, 700);

            } else {

                showMessage(
                    data.message ||
                    "Invalid email or password.",
                    "error"
                );

                loginButton.disabled = false;
                loginButton.textContent = "Login";
            }


        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            showMessage(
                "Unable to connect to the server.",
                "error"
            );

            loginButton.disabled = false;
            loginButton.textContent = "Login";
        }

    });


    // =====================================================
    // Show Message
    // =====================================================

    function showMessage(text, type) {

        message.textContent = text;

        message.className =
            "auth-message " + type;

        message.style.display = "block";
    }

});