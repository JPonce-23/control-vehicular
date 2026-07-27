const loginForm = document.getElementById("loginForm");

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

        mostrarMensaje("Inicio de sesión correcto", "ok");

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1000);

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
});