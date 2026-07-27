const selectVehiculo = document.getElementById("vehiculo_id");
const inputAnio = document.getElementById("anio_gasto");
const btnConsultarResumen = document.getElementById("btnConsultarResumen");
const resumen = document.getElementById("resumen");

const formGasto = document.getElementById("registrar_gasto");
const selectSalida = document.getElementById("salida_id");
const inputFechaGasto = document.getElementById("fecha_gasto");
const inputMonto = document.getElementById("monto");
const selectNivelTanque = document.getElementById("nivel_tanque");
const inputKmOdometro = document.getElementById("km_odometro");
const inputNota = document.getElementById("nota");

const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    colocarAnioActual();
    colocarFechaActual();
    cargarVehiculos();
});

btnConsultarResumen.addEventListener("click", consultarResumen);
formGasto.addEventListener("submit", registrarGastoGasolina);

function colocarAnioActual() {
    const fechaActual = new Date();
    inputAnio.value = fechaActual.getFullYear();
}

function colocarFechaActual() {
    const fechaActual = new Date();
    const anio = fechaActual.getFullYear();
    const mes = String(fechaActual.getMonth() + 1).padStart(2, "0");
    const dia = String(fechaActual.getDate()).padStart(2, "0");

    inputFechaGasto.value = `${anio}-${mes}-${dia}`;
}

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");

        vehiculos.sort((a, b) => a.id - b.id);

        vehiculos.forEach(function (vehiculo) {
            const option = document.createElement("option");

            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;

            selectVehiculo.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function consultarResumen() {
    const vehiculoId = selectVehiculo.value;
    const anio = inputAnio.value;

    if (!vehiculoId) {
        mostrarMensaje(error.message, "Selecciona un vehículo");
        return;
    }

    if (!anio) {
        mostrarMensaje("Ingresa el año", "error");
        return;
    }

    try {
        const resumenCombustible = await apiFetch(
            `/vehiculos/${vehiculoId}/gastos-gasolina/resumen?anio=${anio}`
        );

        mostrarResumen(resumenCombustible);

        await cargarViajesVehiculo(vehiculoId, anio);

        mostrarMensaje("");

    } catch (error) {
        resumen.innerHTML = `
            <h2>Resumen</h2>
            <p>No se pudo cargar el resumen.</p>
        `;

        limpiarSelectSalidas();

        mostrarMensaje(error.message, "error");
    }
}

function mostrarResumen(data) {
    const vehiculo = data.vehiculo;
    const presupuesto = data.presupuesto;
    const ultimoGasto = data.ultimo_gasto;

    resumen.innerHTML = `
        <h2>Resumen</h2>

        <h3>Datos del vehículo</h3>
        <p><strong>Placa:</strong> ${vehiculo.placa || "Sin dato"}</p>
        <p><strong>Vehículo:</strong> ${vehiculo.marca || ""} ${vehiculo.tipo || ""}</p>
        <p><strong>Número de serie:</strong> ${vehiculo.num_serie || "Sin dato"}</p>
        <p><strong>Tarjeta de gasolina:</strong> ${vehiculo.num_tarjeta_gasolina || "Sin dato"}</p>
        <p><strong>Kilometraje acumulado:</strong> ${formatoDineroSimple(vehiculo.km_acumulado)} km</p>

        <h3>Presupuesto</h3>
        <p><strong>Año:</strong> ${presupuesto.anio}</p>
        <p><strong>Monto autorizado total:</strong> ${formatoMoneda(presupuesto.monto_autorizado_total)}</p>
        <p><strong>Monto por mes:</strong> ${formatoMoneda(presupuesto.monto_por_mes)}</p>
        <p><strong>Monto utilizado:</strong> ${formatoMoneda(presupuesto.monto_utilizado)}</p>
        <p><strong>Monto restante:</strong> ${formatoMoneda(presupuesto.monto_restante)}</p>
        <p><strong>Porcentaje restante:</strong> ${presupuesto.porcentaje_restante}%</p>

        <h3>Último gasto</h3>
        <p><strong>Fecha:</strong> ${ultimoGasto.fecha_gasto || "Sin registro"}</p>
        <p><strong>Monto:</strong> ${formatoMoneda(ultimoGasto.monto || 0)}</p>
        <p><strong>Nivel tanque:</strong> ${ultimoGasto.nivel_tanque || "Sin dato"}</p>
        <p><strong>Odómetro:</strong> ${ultimoGasto.km_odometro || "Sin dato"}</p>
    `;
}

async function cargarViajesVehiculo(vehiculoId, anio) {
    try {
        const viajes = await apiFetch(`/vehiculos/${vehiculoId}/viajes?anio=${anio}`);

        limpiarSelectSalidas();

        if (viajes.length === 0) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "No hay salidas para este vehículo en ese año";
            selectSalida.appendChild(option);
            return;
        }

        viajes.forEach(function (viaje) {
            const option = document.createElement("option");

            option.value = viaje.salida_id;

            const fechaSalida = viaje.fecha_salida
                ? viaje.fecha_salida.substring(0, 10)
                : "Sin fecha";

            option.textContent = `Salida #${viaje.salida_id} - ${fechaSalida} - ${viaje.persona || "Sin persona"}`;

            selectSalida.appendChild(option);
        });

    } catch (error) {
        limpiarSelectSalidas();
        mostrarMensaje(error.message, "error");
    }
}

function limpiarSelectSalidas() {
    selectSalida.innerHTML = `
        <option value="">Selecciona una salida</option>
    `;
}

async function registrarGastoGasolina(event) {
    event.preventDefault();

    const vehiculoId = selectVehiculo.value;
    const anio = inputAnio.value;

    if (!vehiculoId) {
        mostrarMensaje("Selecciona un vehículo", "error");
        return;
    }

    if (!anio) {
        mostrarMensaje("Ingresa el año", "error");
        return;
    }

    const datosGasto = {
        salida_id: Number(selectSalida.value),
        fecha_gasto: inputFechaGasto.value,
        monto: Number(inputMonto.value),
        nivel_tanque: selectNivelTanque.value || null,
        km_odometro: inputKmOdometro.value ? Number(inputKmOdometro.value) : null,
        nota: inputNota.value || null
    };

    if (!datosGasto.salida_id) {
        mostrarMensaje("Selecciona una salida relacionada", "error");
        return;
    }

    if (!datosGasto.fecha_gasto) {
        mostrarMensaje("Selecciona la fecha del gasto", "error");
        return;
    }

    if (!datosGasto.monto || datosGasto.monto <= 0) {
        mostrarMensaje("El monto debe ser mayor a cero", "error");
        return;
    }

    try {
        const respuesta = await apiFetch(`/vehiculos/${vehiculoId}/gastos-gasolina`, {
            method: "POST",
            body: JSON.stringify(datosGasto)
        });

        mostrarMensaje(respuesta.mensaje || "Gasto registrado correctamente");

        formGasto.reset();
        colocarFechaActual();

        await consultarResumen();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function formatoMoneda(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN"
    });
}

function formatoDineroSimple(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function mostrarMensaje(texto) {
    mostrarMensaje(error.message, texto);

    setTimeout(function () {
        mostrarMensaje(error.message, "error");
    }, 2000);
}