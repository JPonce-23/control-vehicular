const salidaForm = document.getElementById("salidaForm");
const selectVehiculo = document.getElementById("vehiculo_id");
const selectPersona = document.getElementById("persona_id");
const mensaje = document.getElementById("mensaje");
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


document.addEventListener("DOMContentLoaded", function () {
    cargarVehiculos();
    cargarPersonas();
});

salidaForm.addEventListener("submit", registrarSalida);
selectVehiculo.addEventListener("change", mostrarSaldoTarjetaVehiculo);

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
        fecha_salida: document.getElementById("fecha_salida").value,
        num_oficio: inputNumOficio.value || null,
        num_expediente: inputNumExpediente.value || null,
        area_en_viaje: inputArea.value,
        tipo_movimiento: selectTipoMovimiento.value,
        forma_movimiento: selectFormaMovimiento.value,
        fecha_fin_provisional: document.getElementById("fecha_fin_provisional").value || null,
        fecha_regreso_estimada: inputFechaRegresoEstimada.value,
        monto_agregado_tarjeta: Number(inputMontoAgregadoTarjeta.value || 0),
        finalidad_uso: inputFinalidad.value,
        km_odometro_salida: Number(inputKmSalida.value),
        nivel_gasolina_salida: selectNivelGasolina.value,
        estado_llantas_salida: selectEstadoLlantas.value,
        observaciones: inputObservaciones.value || null,
        observaciones_croquis: inputObservacionesCroquis.value || null
    };

    try {
        const salida = await apiFetch("/salidas/", {
            method: "POST",
            body: JSON.stringify(datosSalida)
        });

        mostrarMensaje("Salida registrada correctamente", "ok");
        localStorage.setItem("salida_id_actual", salida.id);

    } catch (error) {
        mostrarMensaje(error.message, "error");
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