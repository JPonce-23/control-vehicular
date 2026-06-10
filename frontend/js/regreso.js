const regresoForm = document.getElementById("regresoForm");
const selectSalida = document.getElementById("salida_id");
const mensaje = document.getElementById("mensaje");


document.addEventListener("DOMContentLoaded", function () {
    cargarSalidasActivas();
});

regresoForm.addEventListener("submit", registrarRegreso);

async function cargarSalidasActivas() {
    try {
        const salidas = await apiFetch("/salidas/activas/");

        salidas.forEach(function (salida) {
            const option = document.createElement("option");

            option.value = salida.id;
            option.textContent = `Salida #${salida.id} - Vehículo ${salida.vehiculo_id} - Persona ${salida.persona_id}`;

            selectSalida.appendChild(option);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function registrarRegreso(event) {
    event.preventDefault();

    const datosRegreso = {
        salida_id: Number(document.getElementById("salida_id").value),
        capturado_por: 1,
        fecha_regreso: document.getElementById("fecha_regreso").value,
        km_odometro_regreso: Number(document.getElementById("km_odometro_regreso").value),
        nivel_gasolina_regreso: document.getElementById("nivel_gasolina_regreso").value,
        estado_llantas_regreso: document.getElementById("estado_llantas_regreso").value,
        estado_vehiculo_regreso: document.getElementById("estado_vehiculo_regreso").value,
        finalidad_devolucion: document.getElementById("finalidad_devolucion").value,
        observaciones: document.getElementById("observaciones").value
    };

    console.log(datosRegreso);

    try {
        const regreso = await apiFetch("/regresos/", {
            method: "POST",
            body: JSON.stringify(datosRegreso)
        });

        mensaje.textContent = "Regreso registrado correctamente";
        localStorage.setItem("salida_id_actual", datosRegreso.salida_id);

    } catch (error) {
        mensaje.textContent = error.message;
    }
}