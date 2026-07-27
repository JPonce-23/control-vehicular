const selectVehiculo = document.getElementById("vehiculo_id");
const inputAnio = document.getElementById("anio");
const btnConsultarPresupuesto = document.getElementById("btnConsultarPresupuesto");

const detalleVehiculo = document.getElementById("detalleVehiculo");
const resumenPresupuesto = document.getElementById("resumenPresupuesto");

const formPresupuesto = document.getElementById("formPresupuesto");
const inputMontoAutorizadoTotal = document.getElementById("monto_autorizado_total");
const selectMesInicio = document.getElementById("mes_inicio");
const selectMesFin = document.getElementById("mes_fin");
const calculoPresupuesto = document.getElementById("calculoPresupuesto");

const mensaje = document.getElementById("mensaje");

let vehiculosGuardados = [];

const meses = [
    { numero: 1, nombre: "Enero" },
    { numero: 2, nombre: "Febrero" },
    { numero: 3, nombre: "Marzo" },
    { numero: 4, nombre: "Abril" },
    { numero: 5, nombre: "Mayo" },
    { numero: 6, nombre: "Junio" },
    { numero: 7, nombre: "Julio" },
    { numero: 8, nombre: "Agosto" },
    { numero: 9, nombre: "Septiembre" },
    { numero: 10, nombre: "Octubre" },
    { numero: 11, nombre: "Noviembre" },
    { numero: 12, nombre: "Diciembre" }
];

document.addEventListener("DOMContentLoaded", function () {
    colocarAnioActual();
    cargarMeses();
    cargarVehiculos();
});

selectVehiculo.addEventListener("change", mostrarDetalleVehiculo);
btnConsultarPresupuesto.addEventListener("click", consultarPresupuesto);
formPresupuesto.addEventListener("submit", crearPresupuesto);

inputMontoAutorizadoTotal.addEventListener("input", mostrarCalculoPresupuesto);
selectMesInicio.addEventListener("change", mostrarCalculoPresupuesto);
selectMesFin.addEventListener("change", mostrarCalculoPresupuesto);

function colocarAnioActual() {
    const anioActual = new Date().getFullYear();

    inputAnio.innerHTML = `
        <option value="">Selecciona año</option>
        <option value="${anioActual}">${anioActual}</option>
        <option value="${anioActual + 1}">${anioActual + 1}</option>
    `;
}

function cargarMeses() {
    meses.forEach(function (mes) {
        const optionInicio = document.createElement("option");
        optionInicio.value = mes.numero;
        optionInicio.textContent = mes.nombre;
        selectMesInicio.appendChild(optionInicio);

        const optionFin = document.createElement("option");
        optionFin.value = mes.numero;
        optionFin.textContent = mes.nombre;
        selectMesFin.appendChild(optionFin);
    });
}

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");
        vehiculosGuardados = vehiculos;

        selectVehiculo.innerHTML = `
            <option value="">Selecciona un vehículo</option>
        `;

        const vehiculosPermitidos = vehiculos.filter(function (vehiculo) {
            return vehiculo.estado !== "fuera_de_servicio";
        });

        vehiculosPermitidos.sort((a, b) => a.id - b.id);

        vehiculosPermitidos.forEach(function (vehiculo) {
            const option = document.createElement("option");

            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;

            selectVehiculo.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarDetalleVehiculo() {
    const vehiculoId = Number(selectVehiculo.value);

    const vehiculo = vehiculosGuardados.find(function (item) {
        return item.id === vehiculoId;
    });

    if (!vehiculo) {
        detalleVehiculo.innerHTML = `
            <h2>Datos del vehículo</h2>
            <p>Selecciona un vehículo para ver su información.</p>
        `;
        return;
    }

    detalleVehiculo.innerHTML = `
        <h2>Datos del vehículo</h2>

        <table border="1">
            <tr>
                <th>Placa</th>
                <td>${vehiculo.placa || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Marca</th>
                <td>${vehiculo.marca || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Tipo</th>
                <td>${vehiculo.tipo || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Año modelo del vehículo</th>
                <td>${vehiculo.modelo_anio || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Número de serie</th>
                <td>${vehiculo.num_serie || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Tarjeta de gasolina</th>
                <td>${vehiculo.num_tarjeta_gasolina || "Sin dato"}</td>
            </tr>
            <tr>
                <th>Kilometraje acumulado</th>
                <td>${formatoNumero(vehiculo.km_acumulado)} km</td>
            </tr>
            <tr>
                <th>Estado</th>
                <td>${formatearEstado(vehiculo.estado)}</td>
            </tr>
        </table>
    `;
}

async function consultarPresupuesto() {
    const vehiculoId = selectVehiculo.value;
    const anio = inputAnio.value;

    if (!vehiculoId) {
        mostrarMensaje("Selecciona un vehículo", "error");
        return;
    }

    try {
        const presupuesto = await apiFetch(`/vehiculos/${vehiculoId}/presupuesto-gasolina?anio=${anio}`);

        mostrarPresupuesto(presupuesto);
        mostrarMensaje(error.message, "");

    } catch (error) {
        resumenPresupuesto.innerHTML = `
            <h2>Resumen del presupuesto</h2>
            <p>No se encontró presupuesto para este vehículo en el año actual.</p>
        `;

        mostrarMensaje(error.message, "error");
    }
}

async function crearPresupuesto(event) {
    event.preventDefault();

    const vehiculoId = selectVehiculo.value;
    const anio = Number(inputAnio.value);
    const montoAutorizadoTotal = Number(inputMontoAutorizadoTotal.value);
    const mesInicio = Number(selectMesInicio.value);
    const mesFin = Number(selectMesFin.value);

    if (!vehiculoId) {
        mostrarMensaje(error.message, "Slecciona un Vehículo");
        return;
    }

    if (!montoAutorizadoTotal || montoAutorizadoTotal <= 0) {
        mostrarMensaje(error.message, "El monto autorizado total debe ser mayor a cero");
        return;
    }

    if (!mesInicio || !mesFin) {
        mostrarMensaje(error.message, "Selecciona el mes de inicio y el mes de fin");
        return;
    }

    if (mesInicio > mesFin) {
        mostrarMensaje("El mes de inicio no puede ser mayor que el mes de fin", "error");
        return;
    }

    const datosPresupuesto = {
        monto_autorizado_total: montoAutorizadoTotal,
        anio: anio,
        mes_inicio: mesInicio,
        mes_fin: mesFin
    };

    try {
        const presupuesto = await apiFetch(`/vehiculos/${vehiculoId}/presupuesto-gasolina`, {
            method: "POST",
            body: JSON.stringify(datosPresupuesto)
        });

        mostrarMensaje("Presupuesto creado correctamente.");
        mostrarPresupuesto(presupuesto);

        formPresupuesto.reset();

        calculoPresupuesto.innerHTML = `
            <p>Captura monto y rango de meses para calcular el monto mensual.</p>
        `;

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarPresupuesto(presupuesto) {
    const mesInicio = obtenerNombreMes(presupuesto.mes_inicio);
    const mesFin = obtenerNombreMes(presupuesto.mes_fin);

    resumenPresupuesto.innerHTML = `
        <h2>Resumen del presupuesto</h2>

        <p><strong>ID presupuesto:</strong> ${presupuesto.presupuesto_id || presupuesto.id || "Sin dato"}</p>
        <p><strong>Año presupuestal:</strong> ${presupuesto.anio}</p>
        <p><strong>Periodo:</strong> ${mesInicio} a ${mesFin}</p>
        <p><strong>Monto autorizado total:</strong> ${formatoMoneda(presupuesto.monto_autorizado_total)}</p>
        <p><strong>Monto por mes:</strong> ${formatoMoneda(presupuesto.monto_por_mes)}</p>
        <p><strong>Monto utilizado:</strong> ${formatoMoneda(presupuesto.monto_utilizado)}</p>
        <p><strong>Monto restante:</strong> ${formatoMoneda(presupuesto.monto_restante ?? presupuesto.saldo_acumulado)}</p>
        <p><strong>Porcentaje restante:</strong> ${presupuesto.porcentaje_restante ?? calcularPorcentajeRestante(presupuesto)}%</p>
    `;
}

function mostrarCalculoPresupuesto() {
    const montoAutorizadoTotal = Number(inputMontoAutorizadoTotal.value);
    const mesInicio = Number(selectMesInicio.value);
    const mesFin = Number(selectMesFin.value);

    if (!montoAutorizadoTotal || !mesInicio || !mesFin) {
        calculoPresupuesto.innerHTML = `
            <p>Captura monto y rango de meses para calcular el monto mensual.</p>
        `;
        return;
    }

    if (mesInicio > mesFin) {
        calculoPresupuesto.innerHTML = `
            <p>El mes de inicio no puede ser mayor que el mes de fin.</p>
        `;
        return;
    }

    const mesesActivos = mesFin - mesInicio + 1;
    const montoPorMes = montoAutorizadoTotal / mesesActivos;

    calculoPresupuesto.innerHTML = `
        <p><strong>Meses activos:</strong> ${mesesActivos}</p>
        <p><strong>Monto mensual calculado:</strong> ${formatoMoneda(montoPorMes)}</p>
    `;
}

function obtenerNombreMes(numeroMes) {
    const mes = meses.find(function (item) {
        return item.numero === Number(numeroMes);
    });

    return mes ? mes.nombre : "Sin dato";
}

function calcularPorcentajeRestante(presupuesto) {
    const total = Number(presupuesto.monto_autorizado_total || 0);
    const restante = Number(presupuesto.monto_restante ?? presupuesto.saldo_acumulado ?? 0);

    if (total <= 0) {
        return 0;
    }

    return ((restante / total) * 100).toFixed(2);
}

function formatoMoneda(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN"
    });
}

function formatoNumero(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatearEstado(estado) {
    const estados = {
        disponible: "Disponible",
        en_uso: "En uso",
        mantenimiento: "Mantenimiento",
        fuera_de_servicio: "Fuera de servicio"
    };

    return estados[estado] || estado;
}

function mostrarMensaje(texto) {
    mostrarMensaje(error.message, texto);

    setTimeout(function () {
        mostrarMensaje(error.message, " ");
    }, 2500);
}