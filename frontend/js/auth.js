const loginForm = document.getElementById("loginForm");
const mensaje = document.getElementById("mensaje");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const correo = document.getElementById("correo").value;
    const password = document.getElementById("password").value;

    try {
        const data = await apiFetch("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                correo: correo,
                password: password
            })
        });

        localStorage.setItem("token", data.access_token);

        mensaje.textContent = "Inicio de sesión correcto";

        window.location.href = "dashboard.html";

    } catch (error) {
        mensaje.textContent = error.message;
    }
});