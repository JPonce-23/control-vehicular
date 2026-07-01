const tablaVehiculos = document.getElementById("tablaVehiculos");
const mensaje = document.getElementById("mensaje");

const seccionFormulario = document.getElementById("seccionFormulario");
const btnMostrarFormulario = document.getElementById("btnMostrarFormulario");

const formVehiculo = document.getElementById("formVehiculo");
const tituloFormulario = document.getElementById("tituloFormulario");
const btnGuardar = document.getElementById("btnGuardar");
const btnCancelarEdicion = document.getElementById("btnCancelarEdicion");

const inputVehiculoIdEdicion = document.getElementById("vehiculo_id_edicion");
const inputPlaca = document.getElementById("placa");
const inputMarca = document.getElementById("marca");
const inputTipo = document.getElementById("tipo");
const inputModeloAnio = document.getElementById("modelo_anio");
const inputCilindros = document.getElementById("cilindros");
const inputNumSerie = document.getElementById("num_serie");
const inputNumMotor = document.getElementById("num_motor");
const inputNumPoliza = document.getElementById("num_poliza");
const inputNumInventario = document.getElementById("num_inventario");
const inputColor = document.getElementById("color");
const inputNumTarjetaGasolina = document.getElementById("num_tarjeta_gasolina");
const inputSaldoTarjetaGasolina = document.getElementById("saldo_tarjeta_gasolina");
const inputKmAcumulado = document.getElementById("km_acumulado");

let vehiculosGuardados = [];

document.addEventListener("DOMContentLoaded", cargarVehiculos);

btnMostrarFormulario.addEventListener("click", function () {
    limpiarFormulario();
    mostrarFormularioRegistro();
});

formVehiculo.addEventListener("submit", guardarVehiculo);

btnCancelarEdicion.addEventListener("click", function () {
    limpiarFormulario();
    ocultarFormulario();
});

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");

        vehiculosGuardados = vehiculos;
        tablaVehiculos.innerHTML = "";

        if (vehiculos.length === 0) {
            tablaVehiculos.innerHTML = `
                <tr>
                    <td colspan="10">No hay vehículos registrados.</td>
                </tr>
            `;
            return;
        }

        vehiculos.forEach(function (vehiculo) {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${vehiculo.id}</td>
                <td>${vehiculo.placa || ""}</td>
                <td>${vehiculo.marca || ""}</td>
                <td>${vehiculo.tipo || ""}</td>
                <td>${vehiculo.modelo_anio || ""}</td>
                <td>${vehiculo.num_serie || ""}</td>
                <td>${vehiculo.color || ""}</td>
                <td>${formatoNumero(vehiculo.km_acumulado)}</td>
                <td>${formatearEstado(vehiculo.estado)}</td>
                <td>${formatearDinero(vehiculo.saldo_tarjeta_gasolina)}</td>
                <td>
                    <button type="button" onclick="editarVehiculo(${vehiculo.id})">
                        Editar
                    </button>

                    <button type="button" onclick="cambiarEstadoVehiculo(${vehiculo.id}, 'disponible')">
                        Disponible
                    </button>

                    <button type="button" onclick="cambiarEstadoVehiculo(${vehiculo.id}, 'mantenimiento')">
                        Mantenimiento
                    </button>

                    <button type="button" onclick="cambiarEstadoVehiculo(${vehiculo.id}, 'fuera_de_servicio')">
                        Fuera de servicio
                    </button>
                </td>
            `;

            tablaVehiculos.appendChild(fila);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function guardarVehiculo(event) {
    event.preventDefault();

    const vehiculoId = inputVehiculoIdEdicion.value;
    const datosVehiculo = obtenerDatosFormulario();

    try {
        if (vehiculoId) {
            await apiFetch(`/vehiculos/${vehiculoId}`, {
                method: "PUT",
                body: JSON.stringify(datosVehiculo)
            });

            mostrarMensaje("Vehículo actualizado correctamente.");
        } else {
            await apiFetch("/vehiculos/", {
                method: "POST",
                body: JSON.stringify(datosVehiculo)
            });

            mostrarMensaje("Vehículo registrado correctamente.");
        }

        limpiarFormulario();
        ocultarFormulario();
        await cargarVehiculos();

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

function obtenerDatosFormulario() {
    return {
        placa: inputPlaca.value.trim(),
        marca: inputMarca.value.trim(),
        tipo: inputTipo.value.trim(),
        modelo_anio: Number(inputModeloAnio.value),
        cilindros: Number(inputCilindros.value),
        num_serie: inputNumSerie.value.trim(),
        num_motor: inputNumMotor.value.trim() || null,
        num_poliza: inputNumPoliza.value.trim() || null,
        num_inventario: inputNumInventario.value.trim() || null,
        color: inputColor.value.trim(),
        num_tarjeta_gasolina: inputNumTarjetaGasolina.value.trim() || null,
        saldo_tarjeta_gasolina: Number(inputSaldoTarjetaGasolina.value || 0),
        km_acumulado: Number(inputKmAcumulado.value)
    };
}

function editarVehiculo(vehiculoId) {
    const vehiculo = vehiculosGuardados.find(function (item) {
        return item.id === vehiculoId;
    });

    if (!vehiculo) {
        mensaje.textContent = "Vehículo no encontrado.";
        return;
    }

    inputVehiculoIdEdicion.value = vehiculo.id;
    inputPlaca.value = vehiculo.placa || "";
    inputMarca.value = vehiculo.marca || "";
    inputTipo.value = vehiculo.tipo || "";
    inputModeloAnio.value = vehiculo.modelo_anio || "";
    inputCilindros.value = vehiculo.cilindros || "";
    inputNumSerie.value = vehiculo.num_serie || "";
    inputNumMotor.value = vehiculo.num_motor || "";
    inputNumPoliza.value = vehiculo.num_poliza || "";
    inputNumInventario.value = vehiculo.num_inventario || "";
    inputColor.value = vehiculo.color || "";
    inputNumTarjetaGasolina.value = vehiculo.num_tarjeta_gasolina || "";
    inputSaldoTarjetaGasolina.value = vehiculo.saldo_tarjeta_gasolina || 0;
    inputKmAcumulado.value = vehiculo.km_acumulado || 0;

    tituloFormulario.textContent = "Editar vehículo";
    btnGuardar.value = "Guardar cambios";

    seccionFormulario.style.display = "block";
    window.scrollTo(0, document.body.scrollHeight);
}

async function cambiarEstadoVehiculo(vehiculoId, nuevoEstado) {
    const confirmar = confirm(`¿Seguro que deseas cambiar el estado a "${formatearEstado(nuevoEstado)}"?`);

    if (!confirmar) {
        return;
    }

    try {
        await apiFetch(`/vehiculos/${vehiculoId}/estado`, {
            method: "PUT",
            body: JSON.stringify({
                estado: nuevoEstado
            })
        });

        mostrarMensaje("Estado del vehículo actualizado correctamente.");
        await cargarVehiculos();

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

function mostrarFormularioRegistro() {
    tituloFormulario.textContent = "Registrar vehículo";
    btnGuardar.value = "Registrar vehículo";
    seccionFormulario.style.display = "block";
    window.scrollTo(0, document.body.scrollHeight);
}

function ocultarFormulario() {
    seccionFormulario.style.display = "none";
}

function limpiarFormulario() {
    formVehiculo.reset();
    inputVehiculoIdEdicion.value = "";
    tituloFormulario.textContent = "Registrar vehículo";
    btnGuardar.value = "Registrar vehículo";
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

function formatoNumero(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function mostrarMensaje(texto) {
    mensaje.textContent = texto;

    setTimeout(function () {
        mensaje.textContent = "";
    }, 2500);
}


function formatearDinero(valor) {
    const numero = Number(valor || 0);

    return numero.toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN"
    });
}