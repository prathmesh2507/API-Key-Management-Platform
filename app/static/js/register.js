const registerForm = document.getElementById("registerForm");
const errorMsg = document.getElementById("errorMsg");

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        errorMsg.textContent = "Passwords do not match";
        return;
    }

    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            errorMsg.textContent = data.error || "Registration failed";
            return;
        }

        alert("Registration successful! Please login.");
        window.location.href = "/auth/login-page";

    } catch (err) {
        errorMsg.textContent = "Server error";
    }
});
