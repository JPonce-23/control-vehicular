async function obtenerUsuarioActual() {
    return await apiFetch("/usuarios/me");
}

function obtenerRutaLogin() {
    if (window.location.pathname.includes("/pages/")) {
        return "../index.html";
    }

    return "index.html";
}

function obtenerRutaDashboard() {
    if (window.location.pathname.includes("/pages/")) {
        return "../dashboard.html";
    }

    return "dashboard.html";
}

function cerrarSesion() {
    localStorage.removeItem("token");
    window.location.href = obtenerRutaLogin();
}

async function protegerPagina() {
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = obtenerRutaLogin();
        return;
    }

    try {
        const usuario = await obtenerUsuarioActual();

        const rolesPermitidosTexto = document.body.dataset.roles;

        if (rolesPermitidosTexto) {
            const rolesPermitidos = rolesPermitidosTexto.split(",");

            if (!rolesPermitidos.includes(usuario.rol)) {
                alert("No tienes permisos para acceder a esta página.");
                window.location.href = obtenerRutaDashboard();
                return;
            }
        }

        window.usuarioActual = usuario;

        document.dispatchEvent(new CustomEvent("usuario-autenticado", {
            detail: usuario
        }));

    } catch (error) {
        localStorage.removeItem("token");
        window.location.href = obtenerRutaLogin();
    }
}

document.addEventListener("DOMContentLoaded", protegerPagina);