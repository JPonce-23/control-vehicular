const regresoForm = document.getElementById("regresoForm");
const selectSalida = document.getElementById("salida_id");
const mensaje = document.getElementById("mensaje");
const inputSaldoTarjetaRegreso = document.getElementById("saldo_tarjeta_regreso");


document.addEventListener("DOMContentLoaded", function () {
    cargarSalidasActivas();
});

regresoForm.addEventListener("submit", registrarRegreso);

async function cargarSalidasActivas() {
    try {
        const salidas = await apiFetch("/salidas/activas/");
        const vehiculos = await apiFetch("/vehiculos/");
        const personas = await apiFetch("/personas/");

        selectSalida.innerHTML = `
            <option value="">Selecciona una salida</option>
        `;

        if (salidas.length === 0) {
            selectSalida.innerHTML = `
                <option value="">No hay salidas activas</option>
            `;
            return;
        }

        salidas.forEach(function (salida) {
            const vehiculo = vehiculos.find(function (item) {
                return item.id === salida.vehiculo_id;
            });

            const persona = personas.find(function (item) {
                return item.id === salida.persona_id;
            });

            const option = document.createElement("option");

            option.value = salida.id;
            option.textContent = `Salida #${salida.id} - ${obtenerNombreVehiculo(vehiculo)} - ${obtenerNombrePersona(persona)}`;

            selectSalida.appendChild(option);
        });

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function registrarRegreso(event) {
    event.preventDefault();

    const datosRegreso = {
        salida_id: Number(document.getElementById("salida_id").value),
        fecha_regreso: document.getElementById("fecha_regreso").value,
        km_odometro_regreso: Number(document.getElementById("km_odometro_regreso").value),
        nivel_gasolina_regreso: document.getElementById("nivel_gasolina_regreso").value,
        saldo_tarjeta_regreso: Number(inputSaldoTarjetaRegreso.value),
        estado_llantas_regreso: document.getElementById("estado_llantas_regreso").value,
        estado_vehiculo_regreso: document.getElementById("estado_vehiculo_regreso").value,
        finalidad_devolucion: document.getElementById("finalidad_devolucion").value,
        observaciones: document.getElementById("observaciones").value || null
    };


    try {

        const regreso = await apiFetch("/regresos/", {
            method: "POST",
            body: JSON.stringify(datosRegreso)
        });

        mostrarMensaje("Regreso registrado correctamente", "ok");
        localStorage.setItem("salida_id_actual", datosRegreso.salida_id);

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


function obtenerNombreVehiculo(vehiculo) {
    if (!vehiculo) {
        return "Vehículo no encontrado";
    }

    const placa = vehiculo.placa || "Sin placa";
    const marca = vehiculo.marca || "";
    const tipo = vehiculo.tipo || "";

    return `${placa} - ${marca} ${tipo}`.trim();
}

function obtenerNombrePersona(persona) {
    if (!persona) {
        return "Persona no encontrada";
    }

    const partes = [
        persona.nombre,
        persona.apellido_paterno,
        persona.apellido_materno
    ].filter(Boolean);

    return partes.join(" ");
}