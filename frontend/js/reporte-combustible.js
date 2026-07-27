const selectVehiculo = document.getElementById("vehiculo_id");
const inputAnio = document.getElementById("anio_reporte");
const btnConsultarReporte = document.getElementById("btnConsultarReporte");

const resumenVehiculo = document.getElementById("resumenVehiculo");
const tablaReporteMensual = document.getElementById("tablaReporteMensual");
const tablaGastos = document.getElementById("tablaGastos");
const tablaViajes = document.getElementById("tablaViajes");

const graficaCircular = document.getElementById("graficaCircular");
const graficaBarras = document.getElementById("graficaBarras");

const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    colocarAnioActual();
    cargarVehiculos();
});

btnConsultarReporte.addEventListener("click", consultarReporteCompleto);

function colocarAnioActual() {
    const fechaActual = new Date();
    inputAnio.value = fechaActual.getFullYear();
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

async function consultarReporteCompleto() {
    const vehiculoId = selectVehiculo.value;
    const anio = inputAnio.value;

    if (!vehiculoId) {
        mostrarMensaje(error.message, "Selecciona un Vehículo");
        return;
    }

    if (!anio) {
        mostrarMensaje(error.message, "Ingresa el año");
        return;
    }

    try {
        const resumen = await apiFetch(`/vehiculos/${vehiculoId}/gastos-gasolina/resumen?anio=${anio}`);
        const reporte = await apiFetch(`/vehiculos/${vehiculoId}/reporte-combustible?anio=${anio}`);
        const gastos = await apiFetch(`/vehiculos/${vehiculoId}/gastos-gasolina?anio=${anio}`);
        const viajes = await apiFetch(`/vehiculos/${vehiculoId}/viajes?anio=${anio}`);

        mostrarResumen(resumen);
        mostrarTablaReporteMensual(reporte.reporte || []);
        mostrarTablaGastos(gastos || []);
        mostrarTablaViajes(viajes || []);

        dibujarGraficaCircular(resumen.presupuesto);
        dibujarGraficaBarras(reporte.reporte || []);

        mostrarMensaje(error.message, " ");

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function mostrarResumen(data) {
    const vehiculo = data.vehiculo;
    const presupuesto = data.presupuesto;
    const ultimoGasto = data.ultimo_gasto;

    resumenVehiculo.innerHTML = `
        <h2>Resumen del vehículo</h2>

        <h3>Datos del vehículo</h3>
        <p><strong>Placa:</strong> ${vehiculo.placa || "Sin dato"}</p>
        <p><strong>Vehículo:</strong> ${vehiculo.marca || ""} ${vehiculo.tipo || ""}</p>
        <p><strong>Número de serie:</strong> ${vehiculo.num_serie || "Sin dato"}</p>
        <p><strong>Tarjeta de gasolina:</strong> ${vehiculo.num_tarjeta_gasolina || "Sin dato"}</p>
        <p><strong>Kilometraje acumulado:</strong> ${formatoNumero(vehiculo.km_acumulado)} km</p>

        <h3>Presupuesto</h3>
        <p><strong>Año:</strong> ${presupuesto.anio}</p>
        <p><strong>Monto autorizado total:</strong> ${formatoMoneda(presupuesto.monto_autorizado_total)}</p>
        <p><strong>Monto por mes:</strong> ${formatoMoneda(presupuesto.monto_por_mes)}</p>
        <p><strong>Monto utilizado:</strong> ${formatoMoneda(presupuesto.monto_utilizado)}</p>
        <p><strong>Monto restante:</strong> ${formatoMoneda(presupuesto.monto_restante)}</p>
        <p><strong>Porcentaje restante:</strong> ${presupuesto.porcentaje_restante}%</p>

        <h3>Último gasto</h3>
        <p><strong>Fecha:</strong> ${ultimoGasto?.fecha_gasto || "Sin registro"}</p>
        <p><strong>Monto:</strong> ${formatoMoneda(ultimoGasto?.monto || 0)}</p>
        <p><strong>Nivel tanque:</strong> ${ultimoGasto?.nivel_tanque || "Sin dato"}</p>
        <p><strong>Odómetro:</strong> ${ultimoGasto?.km_odometro || "Sin dato"}</p>
    `;
}

function mostrarTablaReporteMensual(reporte) {
    tablaReporteMensual.innerHTML = "";

    if (reporte.length === 0) {
        tablaReporteMensual.innerHTML = `
            <tr>
                <td colspan="6">No hay reporte mensual para mostrar.</td>
            </tr>
        `;
        return;
    }

    reporte.forEach(function (item) {
        const fila = document.createElement("tr");

        fila.innerHTML = `
            <td>${item.mes}</td>
            <td>${formatoMoneda(item.monto_autorizado_mes)}</td>
            <td>${formatoMoneda(item.gasto_mes)}</td>
            <td>${formatoMoneda(item.monto_restante_mes)}</td>
            <td>${formatoMoneda(item.gasto_acumulado)}</td>
            <td>${formatoMoneda(item.monto_restante_total)}</td>
        `;

        tablaReporteMensual.appendChild(fila);
    });
}

function mostrarTablaGastos(gastos) {
    tablaGastos.innerHTML = "";

    if (gastos.length === 0) {
        tablaGastos.innerHTML = `
            <tr>
                <td colspan="7">No hay gastos registrados.</td>
            </tr>
        `;
        return;
    }

    gastos.forEach(function (gasto) {
        const fila = document.createElement("tr");

        fila.innerHTML = `
            <td>${gasto.id}</td>
            <td>${gasto.salida_id}</td>
            <td>${formatearFecha(gasto.fecha_gasto)}</td>
            <td>${formatoMoneda(gasto.monto)}</td>
            <td>${gasto.nivel_tanque || "Sin dato"}</td>
            <td>${gasto.km_odometro || "Sin dato"}</td>
            <td>${gasto.nota || ""}</td>
        `;

        tablaGastos.appendChild(fila);
    });
}

function mostrarTablaViajes(viajes) {
    tablaViajes.innerHTML = "";

    if (viajes.length === 0) {
        tablaViajes.innerHTML = `
            <tr>
                <td colspan="8">No hay viajes registrados para este vehículo.</td>
            </tr>
        `;
        return;
    }

    viajes.forEach(function (viaje) {
        const fila = document.createElement("tr");

        fila.innerHTML = `
            <td>${viaje.salida_id}</td>
            <td>${viaje.persona || "Sin dato"}</td>
            <td>${formatearFecha(viaje.fecha_salida)}</td>
            <td>${formatearFecha(viaje.fecha_regreso)}</td>
            <td>${formatoNumero(viaje.km_salida)}</td>
            <td>${viaje.km_regreso !== null ? formatoNumero(viaje.km_regreso) : "Sin regreso"}</td>
            <td>${viaje.kilometros_recorridos !== null ? formatoNumero(viaje.kilometros_recorridos) : "Sin dato"}</td>
            <td>${viaje.finalidad_uso || ""}</td>
        `;

        tablaViajes.appendChild(fila);
    });
}

function dibujarGraficaCircular(presupuesto) {
    const ctx = graficaCircular.getContext("2d");

    ctx.clearRect(0, 0, graficaCircular.width, graficaCircular.height);

    const porcentajeRestante = Number(presupuesto.porcentaje_restante || 0);
    const porcentajeUtilizado = 100 - porcentajeRestante;

    const centroX = graficaCircular.width / 2;
    const centroY = graficaCircular.height / 2;
    const radio = 100;

    const anguloInicio = -Math.PI / 2;
    const anguloUtilizado = anguloInicio + (2 * Math.PI * porcentajeUtilizado / 100);

    ctx.beginPath();
    ctx.moveTo(centroX, centroY);
    ctx.arc(centroX, centroY, radio, anguloInicio, anguloUtilizado);
    ctx.closePath();
    ctx.fillStyle = "#d9534f";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(centroX, centroY);
    ctx.arc(centroX, centroY, radio, anguloUtilizado, anguloInicio + 2 * Math.PI);
    ctx.closePath();
    ctx.fillStyle = "#5cb85c";
    ctx.fill();

    ctx.fillStyle = "#000";
    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`${porcentajeRestante.toFixed(2)}% restante`, centroX, centroY + 5);

    ctx.textAlign = "left";
    ctx.fillText("Rojo: utilizado", 20, 270);
    ctx.fillText("Verde: restante", 20, 290);
}

function dibujarGraficaBarras(reporte) {
    const ctx = graficaBarras.getContext("2d");

    ctx.clearRect(0, 0, graficaBarras.width, graficaBarras.height);

    if (reporte.length === 0) {
        ctx.font = "16px Arial";
        ctx.fillText("No hay datos para graficar.", 20, 40);
        return;
    }

    const margenIzquierdo = 50;
    const margenInferior = 50;
    const altoGrafica = graficaBarras.height - 80;
    const anchoGrafica = graficaBarras.width - 80;

    const maximo = Math.max(
        ...reporte.map(item => Math.max(
            Number(item.monto_autorizado_mes || 0),
            Number(item.gasto_mes || 0)
        ))
    );

    const anchoGrupo = anchoGrafica / reporte.length;
    const anchoBarra = anchoGrupo / 3;

    ctx.font = "12px Arial";
    ctx.fillStyle = "#000";

    ctx.beginPath();
    ctx.moveTo(margenIzquierdo, 20);
    ctx.lineTo(margenIzquierdo, altoGrafica + 20);
    ctx.lineTo(graficaBarras.width - 20, altoGrafica + 20);
    ctx.stroke();

    reporte.forEach(function (item, index) {
        const xBase = margenIzquierdo + index * anchoGrupo + 10;

        const autorizado = Number(item.monto_autorizado_mes || 0);
        const gasto = Number(item.gasto_mes || 0);

        const altoAutorizado = maximo > 0 ? (autorizado / maximo) * altoGrafica : 0;
        const altoGasto = maximo > 0 ? (gasto / maximo) * altoGrafica : 0;

        const yAutorizado = altoGrafica + 20 - altoAutorizado;
        const yGasto = altoGrafica + 20 - altoGasto;

        ctx.fillStyle = "#0275d8";
        ctx.fillRect(xBase, yAutorizado, anchoBarra, altoAutorizado);

        ctx.fillStyle = "#f0ad4e";
        ctx.fillRect(xBase + anchoBarra + 3, yGasto, anchoBarra, altoGasto);

        ctx.fillStyle = "#000";
        ctx.save();
        ctx.translate(xBase, altoGrafica + 40);
        ctx.rotate(-Math.PI / 4);
        ctx.fillText(item.mes.substring(0, 3), 0, 0);
        ctx.restore();
    });

    ctx.fillStyle = "#000";
    ctx.fillText("Azul: autorizado", 650, 25);
    ctx.fillText("Naranja: gastado", 650, 45);
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

function formatearFecha(fecha) {
    if (!fecha) return "Sin fecha";

    return String(fecha).substring(0, 10);
}