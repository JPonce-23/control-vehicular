const salidaForm = document.getElementById("salidaForm");
const selectVehiculo = document.getElementById("vehiculo_id");
const selectPersona = document.getElementById("persona_id");
const mensaje = document.getElementById("mensaje");

// Campos que pueden estar comentados u opcionales en el HTML:
const inputNumOficio = document.getElementById("num_oficio");
const inputNumExpediente = document.getElementById("num_expediente");
const inputArea = document.getElementById("area_en_viaje");
const selectTipoMovimiento = document.getElementById("tipo_movimiento");
const selectFormaMovimiento = document.getElementById("forma_movimiento");
const inputFechaSalida = document.getElementById("fecha_salida");
const inputFechaFinProvisional = document.getElementById("fecha_fin_provisional");
const inputFinalidad = document.getElementById("finalidad_uso");
const inputKmSalida = document.getElementById("km_odometro_salida");
const selectNivelGasolina = document.getElementById("nivel_gasolina_salida");
const selectEstadoLlantas = document.getElementById("estado_llantas_salida");
const inputObservaciones = document.getElementById("observaciones");
const inputObservacionesCroquis = document.getElementById("observaciones_croquis");
const inputFechaRegresoEstimada = document.getElementById("fecha_regreso_estimada");
const inputMontoAgregadoTarjeta = document.getElementById("monto_agregado_tarjeta");

let vehiculosCargados = [];

const saldoTarjetaVehiculo = document.getElementById("saldoTarjetaVehiculo");
const panelConfirmacion = document.getElementById("panelConfirmacion");
const btnGenerarResguardo = document.getElementById("btnGenerarResguardo");
const btnVolverListado = document.getElementById("btnVolverListado");
const seccionFormulario = salidaForm ? salidaForm.closest("section.card") : null;


document.addEventListener("DOMContentLoaded", function () {
    cargarVehiculos();
    cargarPersonas();
});

if (salidaForm) {
    salidaForm.addEventListener("submit", registrarSalida);
}

if (selectVehiculo) {
    selectVehiculo.addEventListener("change", mostrarSaldoTarjetaVehiculo);
}

if (btnGenerarResguardo) {
    btnGenerarResguardo.addEventListener("click", function () {
        window.location.href = "generacion-resguardo.html";
    });
}

if (btnVolverListado) {
    btnVolverListado.addEventListener("click", function () {
        window.location.href = "../dashboard.html";
    });
}

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");
        vehiculosCargados = vehiculos;
        const disponibles = vehiculos.filter(vehiculo => vehiculo.estado === "disponible");

        disponibles.forEach(vehiculo => {
            const option = document.createElement("option");
            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;
            if (selectVehiculo) selectVehiculo.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarPersonas() {
    try {
        const personas = await apiFetch("/personas/");
        const activas = personas.filter(persona => persona.estado === "activo");

        activas.forEach(persona => {
            const option = document.createElement("option");
            option.value = persona.id;
            option.textContent = `${persona.nombre} ${persona.apellido_paterno} - Licencia ${persona.num_licencia}`;
            if (selectPersona) selectPersona.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function registrarSalida(event) {
    event.preventDefault();

    const datosSalida = {
        vehiculo_id: selectVehiculo ? Number(selectVehiculo.value) : null,
        persona_id: selectPersona ? Number(selectPersona.value) : null,
        fecha_salida: inputFechaSalida ? (inputFechaSalida.value || null) : null,
        num_oficio: inputNumOficio ? (inputNumOficio.value || null) : null,
        num_expediente: inputNumExpediente ? (inputNumExpediente.value || null) : null,
        area_en_viaje: inputArea ? (inputArea.value.trim() || null) : null,
        tipo_movimiento: selectTipoMovimiento ? selectTipoMovimiento.value : "asignacion",
        forma_movimiento: selectFormaMovimiento ? selectFormaMovimiento.value : "provisional",
        fecha_fin_provisional: inputFechaFinProvisional ? (inputFechaFinProvisional.value || null) : null,
        fecha_regreso_estimada: inputFechaRegresoEstimada ? (inputFechaRegresoEstimada.value || null) : null,
        monto_agregado_tarjeta: inputMontoAgregadoTarjeta ? Number(inputMontoAgregadoTarjeta.value || 0) : 0,
        finalidad_uso: inputFinalidad ? inputFinalidad.value : "Operativo",
        km_odometro_salida: inputKmSalida ? Number(inputKmSalida.value) : 0,
        nivel_gasolina_salida: selectNivelGasolina ? selectNivelGasolina.value : "vacio",
        estado_llantas_salida: selectEstadoLlantas ? selectEstadoLlantas.value : "cuarto",
        observaciones: inputObservaciones ? (inputObservaciones.value || null) : null,
        observaciones_croquis: inputObservacionesCroquis ? (inputObservacionesCroquis.value || null) : null
    };

    const btnRegistrar = salidaForm ? salidaForm.querySelector("input[type=submit]") : null;
    if (btnRegistrar) btnRegistrar.disabled = true;

    try {
        const salida = await apiFetch("/salidas/", {
            method: "POST",
            body: JSON.stringify(datosSalida)
        });

        localStorage.setItem("salida_id_actual", salida.id);

        // En lugar de recargar la página, mostramos el modal emergente
        if (panelConfirmacion) {
            panelConfirmacion.style.display = "flex";
        } else {
            // Respaldamos en caso de que no encuentre el modal
            window.location.href = "../dashboard.html";
        }

    } catch (error) {
        mostrarMensaje(error.message, "error");
        if (btnRegistrar) btnRegistrar.disabled = false;
    }
}

function mostrarSaldoTarjetaVehiculo() {
    if (!selectVehiculo || !saldoTarjetaVehiculo) return;

    const vehiculoId = Number(selectVehiculo.value);

    if (!vehiculoId) {
        saldoTarjetaVehiculo.hidden = true;
        saldoTarjetaVehiculo.textContent = "";
        return;
    }

    const vehiculo = vehiculosCargados.find(function (item) {
        return item.id === vehiculoId;
    });

    if (!vehiculo) {
        saldoTarjetaVehiculo.hidden = true;
        saldoTarjetaVehiculo.textContent = "";
        return;
    }

    saldoTarjetaVehiculo.hidden = false;
    saldoTarjetaVehiculo.textContent = `Saldo actual de tarjeta: ${formatearDinero(vehiculo.saldo_tarjeta_gasolina)}`;
}

function formatearDinero(valor) {
    const numero = Number(valor || 0);

    return numero.toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN"
    });
}