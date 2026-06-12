const formAuditoria = document.getElementById("formAuditoria");
const selectVehiculo = document.getElementById("vehiculo_id");
const selectAccion = document.getElementById("accion");

const btnLimpiar = document.getElementById("btnLimpiar");

const resumenAuditoria = document.getElementById("resumenAuditoria");
const tablaAuditoria = document.getElementById("tablaAuditoria");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    cargarVehiculos();
});

formAuditoria.addEventListener("submit", function (event) {
    event.preventDefault();
    consultarAuditoria();
});

btnLimpiar.addEventListener("click", function () {
    selectVehiculo.value = "";
    selectAccion.value = "";

    resumenAuditoria.innerHTML = `
        <h2>Resumen</h2>
        <p>Selecciona un vehículo para consultar sus movimientos.</p>
    `;

    tablaAuditoria.innerHTML = "";
    mensaje.textContent = "";
});

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");

        selectVehiculo.innerHTML = `
            <option value="">Selecciona un vehículo</option>
        `;

        const vehiculosActivos = vehiculos.filter(function (vehiculo) {
            return vehiculo.estado !== "fuera_de_servicio";
        });

        vehiculosActivos.sort((a, b) => a.id - b.id);

        vehiculosActivos.forEach(function (vehiculo) {
            const option = document.createElement("option");

            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;

            selectVehiculo.appendChild(option);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function consultarAuditoria() {
    const vehiculoId = selectVehiculo.value;
    const accion = selectAccion.value;

    if (!vehiculoId) {
        mensaje.textContent = "Selecciona un vehículo.";
        return;
    }

    try {
        mensaje.textContent = "Cargando auditoría...";

        let endpoint = `/historial-salida/auditoria-vehiculo?vehiculo_id=${vehiculoId}`;

        if (accion) {
            endpoint += `&accion=${accion}`;
        }

        const registros = await apiFetch(endpoint);

        mostrarResumen(registros);
        mostrarTablaAuditoria(registros);

        mensaje.textContent = "";

    } catch (error) {
        tablaAuditoria.innerHTML = "";
        mensaje.textContent = error.message;
    }
}

function mostrarResumen(registros) {
    if (!registros || registros.length === 0) {
        resumenAuditoria.innerHTML = `
            <h2>Resumen</h2>
            <p>No hay movimientos registrados para este vehículo.</p>
        `;
        return;
    }

    const primerRegistro = registros[0];

    resumenAuditoria.innerHTML = `
        <h2>Resumen</h2>
        <p><strong>Vehículo:</strong> ${primerRegistro.vehiculo || "Sin dato"}</p>
        <p><strong>Placa:</strong> ${primerRegistro.placa || "Sin dato"}</p>
        <p><strong>Total de movimientos encontrados:</strong> ${registros.length}</p>
    `;
}

function mostrarTablaAuditoria(registros) {
    tablaAuditoria.innerHTML = "";

    if (!registros || registros.length === 0) {
        tablaAuditoria.innerHTML = `
            <tr>
                <td colspan="9">No hay movimientos registrados para este vehículo.</td>
            </tr>
        `;
        return;
    }

    registros.forEach(function (registro) {
        const fila = document.createElement("tr");

        fila.innerHTML = `
            <td>${registro.vehiculo || "Sin dato"}</td>
            <td>${registro.placa || "Sin dato"}</td>
            <td>${registro.persona || "Sin persona"}</td>
            <td>${formatearFechaHora(registro.fecha_salida)}</td>
            <td>${registro.fecha_regreso ? formatearFechaHora(registro.fecha_regreso) : "Sin regreso"}</td>
            <td>${formatearAccion(registro.accion)}</td>
            <td>${registro.descripcion || "Sin descripción"}</td>
            <td>${formatearFechaHora(registro.fecha_movimiento)}</td>
            <td>${registro.usuario || "Usuario no encontrado"}</td>
        `;

        tablaAuditoria.appendChild(fila);
    });
}

function formatearAccion(accion) {
    const acciones = {
        registro_salida: "Registro de salida",
        registro_regreso: "Registro de regreso",
        modificacion: "Modificación / Corrección",
        generacion_resguardo: "Generación de resguardo"
    };

    return acciones[accion] || accion;
}

function formatearFechaHora(fecha) {
    if (!fecha) return "Sin fecha";

    const textoFecha = String(fecha);

    if (textoFecha.includes("T")) {
        return textoFecha.replace("T", " ").substring(0, 16);
    }

    return textoFecha.substring(0, 16);
}