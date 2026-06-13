const formCambiarPassword = document.getElementById("formCambiarPassword");

const inputPasswordActual = document.getElementById("password_actual");
const inputNuevaPassword = document.getElementById("nueva_password");
const inputConfirmarPassword = document.getElementById("confirmar_password");

const mensaje = document.getElementById("mensaje");

formCambiarPassword.addEventListener("submit", cambiarPassword);

async function cambiarPassword(event) {
    event.preventDefault();

    const passwordActual = inputPasswordActual.value;
    const nuevaPassword = inputNuevaPassword.value;
    const confirmarPassword = inputConfirmarPassword.value;

    if (!passwordActual || !nuevaPassword || !confirmarPassword) {
        mensaje.textContent = "Completa todos los campos.";
        return;
    }

    if (nuevaPassword !== confirmarPassword) {
        mensaje.textContent = "La nueva contraseña y la confirmación no coinciden.";
        return;
    }

    if (nuevaPassword.length < 8) {
        mensaje.textContent = "La nueva contraseña debe tener al menos 8 caracteres.";
        return;
    }

    try {
        const respuesta = await apiFetch("/usuarios/me/password", {
            method: "PATCH",
            body: JSON.stringify({
                password_actual: passwordActual,
                nueva_password: nuevaPassword
            })
        });

        mensaje.textContent = respuesta.mensaje || "Contraseña actualizada correctamente.";

        formCambiarPassword.reset();

    } catch (error) {
        mensaje.textContent = error.message;
    }
}