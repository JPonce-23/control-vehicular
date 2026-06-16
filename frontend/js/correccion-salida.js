const resumenSalida = document.getElementById("resumenSalida");
const seccionFormulario = document.getElementById("seccionFormulario");
const formCorreccion = document.getElementById("formCorreccion");

const inputKmSalida = document.getElementById("km_odometro_salida");
const inputKmRegreso = document.getElementById("km_odometro_regreso");

const selectNivelGasolinaSalida = document.getElementById("nivel_gasolina_salida");
const selectNivelGasolinaRegreso = document.getElementById("nivel_gasolina_regreso");

const selectEstadoLlantasSalida = document.getElementById("estado_llantas_salida");
const selectEstadoLlantasRegreso = document.getElementById("estado_llantas_regreso");

const selectEstadoVehiculoRegreso = document.getElementById("estado_vehiculo_regreso");
const selectFinalidadDevolucion = document.getElementById("finalidad_devolucion");

const inputFinalidadUso = document.getElementById("finalidad_uso");
const inputObservacionesSalida = document.getElementById("observaciones_salida");
const inputObservacionesRegreso = document.getElementById("observaciones_regreso");
const inputMotivo = document.getElementById("motivo");

const inputPlacaBusqueda = document.getElementById("placa_busqueda");
const inputPersonaBusqueda = document.getElementById("persona_busqueda");
const btnBuscarCoincidencias = document.getElementById("btnBuscarCoincidencias");
const selectSalida = document.getElementById("salida_id");

const mensaje = document.getElementById("mensaje");

let salidaActual = null;
let regresoActual = null;


formCorreccion.addEventListener("submit", guardarCorreccion);
btnBuscarCoincidencias.addEventListener("click", buscarCoincidenciasSalida);

selectSalida.addEventListener("change", function () {
    if (selectSalida.value) {
        buscarSalida();
    }
});

async function buscarSalida() {
    const salidaId = selectSalida.value;

    if (!salidaId) {
        mensaje.textContent = "Selecciona una salida.";
        return;
    }

    try {
        const salida = await apiFetch(`/salidas/${salidaId}`);
        const regreso = await apiFetch(`/regresos/salida/${salidaId}`);

        salidaActual = salida;
        regresoActual = regreso;

        mostrarResumenSalida(salida, regreso);
        llenarFormulario(salida, regreso);

        seccionFormulario.style.display = "block";
        mensaje.textContent = "";

    } catch (error) {
        salidaActual = null;
        regresoActual = null;
        seccionFormulario.style.display = "none";

        resumenSalida.innerHTML = `
            <h2>Resumen</h2>
            <p>No se pudo consultar la salida o su regreso.</p>
        `;

        mensaje.textContent = error.message;
    }
}

function mostrarResumenSalida(salida, regreso) {
    resumenSalida.innerHTML = `
        <h2>Resumen</h2>

        <p><strong>ID salida:</strong> ${salida.id}</p>
        <p><strong>ID vehículo:</strong> ${salida.vehiculo_id}</p>
        <p><strong>ID persona:</strong> ${salida.persona_id}</p>
        <p><strong>Fecha de salida:</strong> ${formatearFechaHora(salida.fecha_salida)}</p>
        <p><strong>Fecha de regreso:</strong> ${formatearFechaHora(regreso.fecha_regreso)}</p>
        <p><strong>Finalidad de uso:</strong> ${salida.finalidad_uso || "Sin dato"}</p>
        <p><strong>Finalidad de devolución:</strong> ${regreso.finalidad_devolucion || "Sin dato"}</p>
    `;
}

function llenarFormulario(salida, regreso) {
    inputKmSalida.value = salida.km_odometro_salida || "";
    inputKmRegreso.value = regreso.km_odometro_regreso || "";

    selectNivelGasolinaSalida.value = salida.nivel_gasolina_salida || "";
    selectNivelGasolinaRegreso.value = regreso.nivel_gasolina_regreso || "";

    selectEstadoLlantasSalida.value = salida.estado_llantas_salida || "";
    selectEstadoLlantasRegreso.value = regreso.estado_llantas_regreso || "";

    selectEstadoVehiculoRegreso.value = regreso.estado_vehiculo_regreso || "";
    selectFinalidadDevolucion.value = regreso.finalidad_devolucion || "";

    inputFinalidadUso.value = salida.finalidad_uso || "";
    inputObservacionesSalida.value = salida.observaciones || "";
    inputObservacionesRegreso.value = regreso.observaciones || "";

    inputMotivo.value = "";
}

async function guardarCorreccion(event) {
    event.preventDefault();

    if (!salidaActual || !regresoActual) {
        mensaje.textContent = "Primero consulta una salida con regreso registrado.";
        return;
    }

    if (!inputMotivo.value.trim()) {
        mensaje.textContent = "El motivo de corrección es obligatorio.";
        return;
    }

    const datosCorreccion = {
        motivo: inputMotivo.value.trim(),
        km_odometro_salida: Number(inputKmSalida.value),
        km_odometro_regreso: Number(inputKmRegreso.value),
        nivel_gasolina_salida: selectNivelGasolinaSalida.value,
        nivel_gasolina_regreso: selectNivelGasolinaRegreso.value,
        estado_llantas_salida: selectEstadoLlantasSalida.value,
        estado_llantas_regreso: selectEstadoLlantasRegreso.value,
        estado_vehiculo_regreso: selectEstadoVehiculoRegreso.value,
        finalidad_uso: inputFinalidadUso.value.trim(),
        finalidad_devolucion: selectFinalidadDevolucion.value,
        observaciones_salida: inputObservacionesSalida.value.trim() || null,
        observaciones_regreso: inputObservacionesRegreso.value.trim() || null
    };

    try {
        const respuesta = await apiFetch(`/salidas/${salidaActual.id}/correccion-administrativa`, {
            method: "PATCH",
            body: JSON.stringify(datosCorreccion)
        });

        mensaje.textContent = respuesta.mensaje || "Corrección administrativa guardada correctamente.";

        await buscarSalida();

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

function formatearFechaHora(fecha) {
    if (!fecha) return "Sin fecha";

    return String(fecha).replace("T", " ").substring(0, 16);
}


async function buscarCoincidenciasSalida() {
    const placa = inputPlacaBusqueda.value.trim();
    const persona = inputPersonaBusqueda.value.trim();

    if (!placa && !persona) {
        mensaje.textContent = "Ingresa la placa del vehículo o el nombre de la persona.";
        return;
    }

    const parametros = new URLSearchParams();

    if (placa) {
        parametros.append("placa", placa);
    }

    if (persona) {
        parametros.append("persona", persona);
    }

    try {
        const resultados = await apiFetch(`/salidas/buscar-correccion?${parametros.toString()}`);

        selectSalida.innerHTML = `
            <option value="">Selecciona una salida</option>
        `;

        if (resultados.length === 0) {
            selectSalida.innerHTML = `
                <option value="">No se encontraron salidas con regreso</option>
            `;
            mensaje.textContent = "No se encontraron coincidencias.";
            return;
        }

        resultados.forEach(function (item) {
            const option = document.createElement("option");

            option.value = item.salida_id;

            option.textContent = `Salida #${item.salida_id} - ${item.placa} - ${item.vehiculo} - ${item.persona} - Salió: ${formatearFechaHora(item.fecha_salida)} - Regresó: ${formatearFechaHora(item.fecha_regreso)}`;

            selectSalida.appendChild(option);
        });

        mensaje.textContent = `Se encontraron ${resultados.length} salida(s). Selecciona la que deseas corregir.`;

    } catch (error) {
        mensaje.textContent = error.message;
    }
}