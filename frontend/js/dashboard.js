const nombreUsuario = document.getElementById("nombreUsuario");
const rolUsuario = document.getElementById("rolUsuario");
const btnCerrarSesion = document.getElementById("btnCerrarSesion");

document.addEventListener("usuario-autenticado", function (event) {
    const usuario = event.detail;

    mostrarDatosUsuario(usuario);
    aplicarMenuPorRol(usuario.rol);
});

if (btnCerrarSesion) {
    btnCerrarSesion.addEventListener("click", cerrarSesion);
}

function mostrarDatosUsuario(usuario) {
    if (nombreUsuario) {
        nombreUsuario.textContent = `${usuario.nombre} ${usuario.apellido_paterno}`;
    }

    if (rolUsuario) {
        rolUsuario.textContent = formatearRol(usuario.rol);
    }
}

function aplicarMenuPorRol(rol) {
    const elementos = document.querySelectorAll("[data-menu-roles]");

    elementos.forEach(function (elemento) {
        const rolesPermitidos = elemento.dataset.menuRoles.split(",");

        if (!rolesPermitidos.includes(rol)) {
            elemento.style.display = "none";
        }
    });
}

function formatearRol(rol) {
    const roles = {
        administrador: "Administrador",
        capturista: "Capturista"
    };

    return roles[rol] || rol;
}