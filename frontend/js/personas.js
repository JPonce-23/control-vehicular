const tablaPersonas = document.getElementById("tablaPersonas");
const mensaje = document.getElementById("mensaje");

const seccionFormulario = document.getElementById("seccionFormulario");
const btnMostrarFormulario = document.getElementById("btnMostrarFormulario");

const formPersona = document.getElementById("formPersona");
const tituloFormulario = document.getElementById("tituloFormulario");
const btnGuardar = document.getElementById("btnGuardar");
const btnCancelarEdicion = document.getElementById("btnCancelarEdicion");

const inputPersonaIdEdicion = document.getElementById("persona_id_edicion");
const inputNombre = document.getElementById("nombre");
const inputApellidoPaterno = document.getElementById("apellido_paterno");
const inputApellidoMaterno = document.getElementById("apellido_materno");
const inputCargo = document.getElementById("cargo");
const inputRfc = document.getElementById("rfc");
const inputNumLicencia = document.getElementById("num_licencia");
const inputTipoLicencia = document.getElementById("tipo_licencia");
const inputVigenciaLicencia = document.getElementById("vigencia_licencia");

let personasGuardadas = [];

document.addEventListener("DOMContentLoaded", cargarPersonas);

btnMostrarFormulario.addEventListener("click", function () {
    limpiarFormulario();
    mostrarFormularioRegistro();
});

formPersona.addEventListener("submit", guardarPersona);

btnCancelarEdicion.addEventListener("click", function () {
    limpiarFormulario();
    ocultarFormulario();
});

async function cargarPersonas() {
    try {
        const personas = await apiFetch("/personas/");

        personasGuardadas = personas;
        tablaPersonas.innerHTML = "";

        if (personas.length === 0) {
            tablaPersonas.innerHTML = `
                <tr>
                    <td colspan="8">No hay personas registradas.</td>
                </tr>
            `;
            return;
        }

        personas.forEach(function (persona) {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${persona.id}</td>
                <td>${obtenerNombreCompleto(persona)}</td>
                <td>${persona.cargo || ""}</td>
                <td>${persona.rfc || ""}</td>
                <td>${persona.num_licencia || ""}</td>
                <td>${persona.tipo_licencia || ""}</td>
                <td>${persona.vigencia_licencia || ""}</td>
                <td>${formatearEstado(persona.estado)}</td>
                <td>
                    <button type="button" onclick="editarPersona(${persona.id})">
                        Editar
                    </button>

                    <button type="button" onclick="cambiarEstadoPersona(${persona.id}, 'activo')">
                        Activar
                    </button>

                    <button type="button" onclick="cambiarEstadoPersona(${persona.id}, 'suspendido')">
                        Suspender
                    </button>
                </td>
            `;

            tablaPersonas.appendChild(fila);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function guardarPersona(event) {
    event.preventDefault();

    const personaId = inputPersonaIdEdicion.value;
    console.log("ID en edición:", personaId);
    const datosPersona = obtenerDatosFormulario();

    try {
        if (personaId) {
            await apiFetch(`/personas/${personaId}`, {
                method: "PUT",
                body: JSON.stringify(datosPersona)
            });

            mostrarMensaje("Persona actualizada correctamente.");
        } else {
            await apiFetch("/personas/", {
                method: "POST",
                body: JSON.stringify({
                    ...datosPersona,
                    estado: "activo"
                })
            });

            mostrarMensaje("Persona registrada correctamente.");
        }

        limpiarFormulario();
        ocultarFormulario();
        await cargarPersonas();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function obtenerDatosFormulario() {
    return {
        nombre: inputNombre.value.trim(),
        apellido_paterno: inputApellidoPaterno.value.trim(),
        apellido_materno: inputApellidoMaterno.value.trim() || null,
        cargo: inputCargo.value.trim(),
        rfc: inputRfc.value.trim() || null,
        num_licencia: inputNumLicencia.value.trim() || null,
        tipo_licencia: inputTipoLicencia.value.trim() || null,
        vigencia_licencia: inputVigenciaLicencia.value || null
    };
}

function editarPersona(personaId) {
    const persona = personasGuardadas.find(function (item) {
        return item.id === personaId;
    });

    if (!persona) {
        mostrarMensaje("Persona no encontrada", "error");
        return;
    }

    inputPersonaIdEdicion.value = persona.id;

    inputNombre.value = persona.nombre || "";
    inputApellidoPaterno.value = persona.apellido_paterno || "";
    inputApellidoMaterno.value = persona.apellido_materno || "";
    inputCargo.value = persona.cargo || "";
    inputRfc.value = persona.rfc || "";
    inputNumLicencia.value = persona.num_licencia || "";
    inputTipoLicencia.value = persona.tipo_licencia || "";
    inputVigenciaLicencia.value = persona.vigencia_licencia || "";

    tituloFormulario.textContent = "Editar persona autorizada";
    btnGuardar.value = "Guardar cambios";

    seccionFormulario.style.display = "block";
    window.scrollTo(0, document.body.scrollHeight);
}

async function cambiarEstadoPersona(personaId, nuevoEstado) {
    const confirmar = confirm(`¿Seguro que deseas cambiar el estado a "${formatearEstado(nuevoEstado)}"?`);

    if (!confirmar) {
        return;
    }

    try {
        await apiFetch(`/personas/${personaId}/estado`, {
            method: "PUT",
            body: JSON.stringify({
                estado: nuevoEstado
            })
        });

        mostrarMensaje("Estado de la persona actualizado correctamente.");
        await cargarPersonas();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarFormularioRegistro() {
    tituloFormulario.textContent = "Registrar persona autorizada";
    btnGuardar.value = "Registrar persona";
    seccionFormulario.style.display = "block";
    window.scrollTo(0, document.body.scrollHeight);
}

function ocultarFormulario() {
    seccionFormulario.style.display = "none";
}

function limpiarFormulario() {
    formPersona.reset();
    inputPersonaIdEdicion.value = "";
    tituloFormulario.textContent = "Registrar persona autorizada";
    btnGuardar.value = "Registrar persona";
}

function obtenerNombreCompleto(persona) {
    const partes = [
        persona.nombre,
        persona.apellido_paterno,
        persona.apellido_materno
    ].filter(Boolean);

    return partes.join(" ");
}

function formatearEstado(estado) {
    const estados = {
        activo: "Activo",
        suspendido: "Suspendido"
    };

    return estados[estado] || estado;
}

function mostrarMensaje(texto) {
    mostrarMensaje(error.message, texto);

    setTimeout(function () {
        mostrarMensaje(error.message, "");
    }, 2500);
}