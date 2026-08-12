const selectSalida = document.getElementById("salida_id");
const seccionResumen = document.getElementById("resumenSalida");
const resumenTexto = document.getElementById("resumenTexto");
const seccionFormulario = document.getElementById("seccionFormulario");
const formCancelacion = document.getElementById("formCancelacion");
const inputMotivo = document.getElementById("motivo");
const mensaje = document.getElementById("mensaje");

let salidasActivas = [];

document.addEventListener("DOMContentLoaded", cargarSalidasActivas);

selectSalida.addEventListener("change", mostrarResumenSalida);
formCancelacion.addEventListener("submit", confirmarCancelacion);

async function cargarSalidasActivas() {
    try {
        salidasActivas = await apiFetch("/salidas/activas-para-cancelacion");

        selectSalida.innerHTML = `<option value="">Selecciona una salida</option>`;

        if (salidasActivas.length === 0) {
            selectSalida.innerHTML = `<option value="">No hay salidas activas</option>`;
            return;
        }

        salidasActivas.forEach(function (s) {
            const option = document.createElement("option");
            option.value = s.salida_id;
            option.textContent =
                `${s.placa} - ${s.vehiculo} - ${s.persona} - ${formatearFecha(s.fecha_salida)}`;
            selectSalida.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarResumenSalida() {
    const salidaId = selectSalida.value;

    if (!salidaId) {
        seccionResumen.style.display = "none";
        seccionFormulario.style.display = "none";
        return;
    }

    const salida = salidasActivas.find(function (s) {
        return s.salida_id === Number(salidaId);
    });

    if (!salida) {
        return;
    }

    resumenTexto.textContent =
        `Vehículo: ${salida.vehiculo} (${salida.placa}) — ` +
        `Persona: ${salida.persona} — ` +
        `Fecha de salida: ${formatearFecha(salida.fecha_salida)}`;

    seccionResumen.style.display = "block";
    seccionFormulario.style.display = "block";
    inputMotivo.value = "";
}

async function confirmarCancelacion(event) {
    event.preventDefault();

    const salidaId = selectSalida.value;

    if (!salidaId) {
        mostrarMensaje("Selecciona una salida antes de continuar.", "error");
        return;
    }

    if (!inputMotivo.value.trim()) {
        mostrarMensaje("El motivo de la cancelación es obligatorio.", "error");
        return;
    }

    const confirmar = confirm("¿Seguro que deseas cancelar esta salida? Esta acción no se puede deshacer.");

    if (!confirmar) {
        return;
    }

    try {
        await apiFetch(`/salidas/${salidaId}/cancelacion`, {
            method: "PATCH",
            body: JSON.stringify({ motivo: inputMotivo.value.trim() })
        });

        mostrarMensaje("Salida cancelada correctamente. Vehículo y persona quedaron disponibles.");

        seccionResumen.style.display = "none";
        seccionFormulario.style.display = "none";

        await cargarSalidasActivas();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function formatearFecha(fecha) {
    if (!fecha) return "";
    const d = new Date(fecha);
    return d.toLocaleDateString("es-MX");
}