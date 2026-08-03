const salidaForm = document.getElementById("salidaForm");
const selectVehiculo = document.getElementById("vehiculo_id");
const selectPersona = document.getElementById("persona_id");
const mensaje = document.getElementById("mensaje");
const inputArea = document.getElementById("area_en_viaje");
const selectTipoMovimiento = document.getElementById("tipo_movimiento");
const selectFormaMovimiento = document.getElementById("forma_movimiento");
const inputFechaSalida = document.getElementById("fecha_salida");
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
const seccionFormulario = salidaForm.closest("section.card");


document.addEventListener("DOMContentLoaded", function () {
    cargarVehiculos();
    cargarPersonas();
});

salidaForm.addEventListener("submit", registrarSalida);
selectVehiculo.addEventListener("change", mostrarSaldoTarjetaVehiculo);

btnGenerarResguardo.addEventListener("click", function () {
    window.location.href = "generacion-resguardo.html";
});

btnVolverListado.addEventListener("click", function () {
    window.location.href = "../dashboard.html";
});

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");
        vehiculosCargados = vehiculos;
        const disponibles = vehiculos.filter(vehiculo => vehiculo.estado === "disponible");

        disponibles.forEach(vehiculo => {
            const option = document.createElement("option");
            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;
            selectVehiculo.appendChild(option);
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
            selectPersona.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function registrarSalida(event) {
    event.preventDefault();

    const datosSalida = {
        vehiculo_id: Number(selectVehiculo.value),
        persona_id: Number(selectPersona.value),
        fecha_salida: inputFechaSalida.value || null,
        num_oficio: inputNumOficio.value || null,
        num_expediente: inputNumExpediente.value || null,
        area_en_viaje: inputArea.value.trim() || null,
        tipo_movimiento: selectTipoMovimiento.value,
        forma_movimiento: selectFormaMovimiento.value,
        fecha_fin_provisional: null,
        fecha_regreso_estimada: inputFechaRegresoEstimada.value || null,
        monto_agregado_tarjeta: Number(inputMontoAgregadoTarjeta.value || 0),
        finalidad_uso: inputFinalidad.value,
        km_odometro_salida: Number(inputKmSalida.value),
        nivel_gasolina_salida: selectNivelGasolina.value,
        estado_llantas_salida: selectEstadoLlantas.value,
        observaciones: inputObservaciones.value || null,
        observaciones_croquis: inputObservacionesCroquis.value || null
    };

    const btnRegistrar = salidaForm.querySelector("input[type=submit]");
    if (btnRegistrar) btnRegistrar.disabled = true;

    try {
        const salida = await apiFetch("/salidas/", {
            method: "POST",
            body: JSON.stringify(datosSalida)
        });

        localStorage.setItem("salida_id_actual", salida.id);
        recargarConMensaje("Registro completado: salida registrada correctamente.");

    } catch (error) {
        mostrarMensaje(error.message, "error");
        if (btnRegistrar) btnRegistrar.disabled = false;
    }
}

function mostrarSaldoTarjetaVehiculo() {
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