const tablaUsuarios = document.getElementById("tablaUsuarios");
const mensaje = document.getElementById("mensaje");

const seccionFormulario = document.getElementById("seccionFormulario");
const btnMostrarFormulario = document.getElementById("btnMostrarFormulario");

const formUsuario = document.getElementById("formUsuario");
const tituloFormulario = document.getElementById("tituloFormulario");
const btnGuardar = document.getElementById("btnGuardar");
const btnCancelar = document.getElementById("btnCancelar");

const inputUsuarioIdEdicion = document.getElementById("usuario_id_edicion");
const inputNombre = document.getElementById("nombre");
const inputApellidoPaterno = document.getElementById("apellido_paterno");
const inputApellidoMaterno = document.getElementById("apellido_materno");
const inputNumEmpleado = document.getElementById("num_empleado");
const inputCorreo = document.getElementById("correo");
const inputPassword = document.getElementById("password");
const contenedorPassword = document.getElementById("contenedorPassword");

const seccionPasswordTemporal = document.getElementById("seccionPasswordTemporal");
const usuarioTemporalId = document.getElementById("usuarioTemporalId");
const passwordTemporal = document.getElementById("passwordTemporal");

let usuariosGuardados = [];

document.addEventListener("DOMContentLoaded", cargarUsuarios);

btnMostrarFormulario.addEventListener("click", function () {
    limpiarFormulario();
    mostrarFormularioCrear();
});

btnCancelar.addEventListener("click", function () {
    limpiarFormulario();
    ocultarFormulario();
});

formUsuario.addEventListener("submit", guardarUsuario);

async function cargarUsuarios() {
    try {
        const usuarios = await apiFetch("/usuarios/");

        usuariosGuardados = usuarios;
        tablaUsuarios.innerHTML = "";

        if (usuarios.length === 0) {
            tablaUsuarios.innerHTML = `
                <tr>
                    <td colspan="9">No hay usuarios registrados.</td>
                </tr>
            `;
            return;
        }

        usuarios.forEach(function (usuario) {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${usuario.id}</td>
                <td>${obtenerNombreCompleto(usuario)}</td>
                <td>${usuario.num_empleado || ""}</td>
                <td>${usuario.correo || ""}</td>
                <td>${formatearRol(usuario.rol)}</td>
                <td>${formatearEstado(usuario.estado)}</td>
                <td>${formatearFecha(usuario.fecha_alta)}</td>
                <td>${formatearFecha(usuario.ultimo_acceso)}</td>
                <td>
                    <button type="button" onclick="editarUsuario(${usuario.id})">
                        Editar
                    </button>

                    <button type="button" onclick="cambiarRolUsuario(${usuario.id}, 'administrador')">
                        Hacer administrador
                    </button>

                    <button type="button" onclick="cambiarRolUsuario(${usuario.id}, 'capturista')">
                        Hacer capturista
                    </button>

                    <button type="button" onclick="cambiarEstadoUsuario(${usuario.id}, 'activo')">
                        Activar
                    </button>

                    <button type="button" onclick="cambiarEstadoUsuario(${usuario.id}, 'suspendido')">
                        Suspender
                    </button>

                    <button type="button" onclick="generarPasswordTemporal(${usuario.id})">
                        Contraseña temporal
                    </button>
                </td>
            `;

            tablaUsuarios.appendChild(fila);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function guardarUsuario(event) {
    event.preventDefault();

    const usuarioId = inputUsuarioIdEdicion.value;

    try {
        if (usuarioId) {
            const datosUsuario = obtenerDatosEdicion();

            await apiFetch(`/usuarios/${usuarioId}`, {
                method: "PUT",
                body: JSON.stringify(datosUsuario)
            });

            mostrarMensaje("Usuario actualizado correctamente.");
        } else {
            const datosUsuario = obtenerDatosCreacion();

            if (!datosUsuario.password) {
                mostrarMensaje("Ingresa una contraseña para el nuevo usuario.", "error");
                return;
            }

            await apiFetch("/usuarios/", {
                method: "POST",
                body: JSON.stringify(datosUsuario)
            });

            mostrarMensaje("Usuario creado correctamente.");
        }

        limpiarFormulario();
        ocultarFormulario();
        await cargarUsuarios();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function obtenerDatosCreacion() {
    return {
        nombre: inputNombre.value.trim(),
        apellido_paterno: inputApellidoPaterno.value.trim(),
        apellido_materno: inputApellidoMaterno.value.trim() || null,
        num_empleado: inputNumEmpleado.value.trim(),
        correo: inputCorreo.value.trim(),
        password: inputPassword.value
    };
}

function obtenerDatosEdicion() {
    return {
        nombre: inputNombre.value.trim(),
        apellido_paterno: inputApellidoPaterno.value.trim(),
        apellido_materno: inputApellidoMaterno.value.trim() || null,
        num_empleado: inputNumEmpleado.value.trim(),
        correo: inputCorreo.value.trim()
    };
}

function editarUsuario(usuarioId) {
    const usuario = usuariosGuardados.find(function (item) {
        return item.id === usuarioId;
    });

    if (!usuario) {
        mostrarMensaje("Usuario no encontrado.", "error");
        return;
    }

    inputUsuarioIdEdicion.value = usuario.id;
    inputNombre.value = usuario.nombre || "";
    inputApellidoPaterno.value = usuario.apellido_paterno || "";
    inputApellidoMaterno.value = usuario.apellido_materno || "";
    inputNumEmpleado.value = usuario.num_empleado || "";
    inputCorreo.value = usuario.correo || "";

    tituloFormulario.textContent = "Editar usuario";
    btnGuardar.value = "Guardar cambios";

    contenedorPassword.style.display = "none";
    inputPassword.required = false;
    inputPassword.value = "";

    seccionFormulario.style.display = "block";
    window.scrollTo(0, document.body.scrollHeight);
}

async function cambiarRolUsuario(usuarioId, nuevoRol) {
    const confirmar = confirm(`¿Seguro que deseas cambiar el rol a "${formatearRol(nuevoRol)}"?`);

    if (!confirmar) {
        return;
    }

    try {
        await apiFetch(`/usuarios/${usuarioId}/rol`, {
            method: "PUT",
            body: JSON.stringify({
                rol: nuevoRol
            })
        });

        mostrarMensaje("Rol actualizado correctamente.");
        await cargarUsuarios();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cambiarEstadoUsuario(usuarioId, nuevoEstado) {
    const confirmar = confirm(`¿Seguro que deseas cambiar el estado a "${formatearEstado(nuevoEstado)}"?`);

    if (!confirmar) {
        return;
    }

    try {
        await apiFetch(`/usuarios/${usuarioId}/estado`, {
            method: "PATCH",
            body: JSON.stringify({
                estado: nuevoEstado
            })
        });

        mostrarMensaje("Estado actualizado correctamente.");
        await cargarUsuarios();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function generarPasswordTemporal(usuarioId) {
    const confirmar = confirm("¿Seguro que deseas generar una nueva contraseña temporal para este usuario?");

    if (!confirmar) {
        return;
    }

    try {
        const respuesta = await apiFetch(`/usuarios/${usuarioId}/reset-password`, {
            method: "PATCH"
        });

        usuarioTemporalId.textContent = respuesta.usuario_id;
        passwordTemporal.textContent = respuesta.password_temporal;
        seccionPasswordTemporal.style.display = "block";

        mostrarMensaje(respuesta.mensaje || "Contraseña temporal generada correctamente.");

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarFormularioCrear() {
    tituloFormulario.textContent = "Crear usuario";
    btnGuardar.value = "Crear usuario";

    contenedorPassword.style.display = "block";
    inputPassword.required = true;

    seccionPasswordTemporal.style.display = "none";
    seccionFormulario.style.display = "block";

    window.scrollTo(0, document.body.scrollHeight);
}

function ocultarFormulario() {
    seccionFormulario.style.display = "none";
}

function limpiarFormulario() {
    formUsuario.reset();
    inputUsuarioIdEdicion.value = "";
    mensaje.textContent = "";

    tituloFormulario.textContent = "Crear usuario";
    btnGuardar.value = "Crear usuario";

    contenedorPassword.style.display = "block";
    inputPassword.required = false;
}

function obtenerNombreCompleto(usuario) {
    const partes = [
        usuario.nombre,
        usuario.apellido_paterno,
        usuario.apellido_materno
    ].filter(Boolean);

    return partes.join(" ");
}

function formatearRol(rol) {
    const roles = {
        administrador: "Administrador",
        capturista: "Capturista"
    };

    return roles[rol] || rol;
}

function formatearEstado(estado) {
    const estados = {
        activo: "Activo",
        suspendido: "Suspendido"
    };

    return estados[estado] || estado;
}

function formatearFecha(fecha) {
    if (!fecha) return "Sin registro";

    return String(fecha).replace("T", " ").substring(0, 16);
}

function mostrarMensaje(texto) {
    mostrarMensaje(error.message, texto);

    setTimeout(function () {
        mostrarMensaje(error.message, " ");
    }, 2500);
}