const selectSalida = document.getElementById("salida_id");
const condicionesContainer = document.getElementById("condicionesContainer");
const btnGuardarCondiciones = document.getElementById("btnGuardarCondiciones");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    cargarSalidas();
});

selectSalida.addEventListener("change", cargarCondiciones);
btnGuardarCondiciones.addEventListener("click", guardarCondiciones);

async function cargarSalidas() {
    try {
        const salidas = await apiFetch("/salidas/");

        salidas.sort((a, b) => b.id - a.id);

        salidas.forEach(function (salida) {
            const option = document.createElement("option");

            option.value = salida.id;
            option.textContent = `Salida #${salida.id} - Vehículo #${salida.vehiculo_id} - Persona #${salida.persona_id}`;

            selectSalida.appendChild(option);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function cargarCondiciones() {
    const salidaId = selectSalida.value;

    if (!salidaId) {
        condicionesContainer.innerHTML = "Selecciona una salida para cargar las condiciones.";
        return;
    }

    try {
        const condiciones = await apiFetch(`/salidas/${salidaId}/condicion`);

        condicionesContainer.innerHTML = "";

        condiciones.forEach(function (condicion) {
            const div = document.createElement("div");

            div.classList.add("condicion-item");
            div.dataset.itemId = condicion.item_condicion_id;

            div.innerHTML = `
                <p><strong>${formatearNombre(condicion.nombre)}</strong></p>

                <label>
                    <input type="radio" name="condicion_${condicion.item_condicion_id}" value="bueno"
                        ${condicion.estado === "bueno" ? "checked" : ""}>
                    Bueno
                </label>

                <label>
                    <input type="radio" name="condicion_${condicion.item_condicion_id}" value="regular"
                        ${condicion.estado === "regular" ? "checked" : ""}>
                    Regular
                </label>

                <label>
                    <input type="radio" name="condicion_${condicion.item_condicion_id}" value="malo"
                        ${condicion.estado === "malo" ? "checked" : ""}>
                    Malo
                </label>

                <br>

                <label>Observaciones:</label>
                <input 
                    type="text" 
                    class="observacion-condicion" 
                    value="${condicion.observaciones || ""}"
                >

                <hr>
            `;

            condicionesContainer.appendChild(div);
        });

        mensaje.textContent = "";

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function guardarCondiciones() {


    const salidaId = selectSalida.value;

    if (!salidaId) {
        mensaje.textContent = "Selecciona una salida primero";
        return;
    }

    const items = document.querySelectorAll(".condicion-item");

    const condiciones = [];

    items.forEach(function (item) {
        const itemCondicionId = Number(item.dataset.itemId);

        const radioSeleccionado = item.querySelector(
            `input[name="condicion_${itemCondicionId}"]:checked`
        );

        const observaciones = item.querySelector(".observacion-condicion").value;

        condiciones.push({
            item_condicion_id: itemCondicionId,
            estado: radioSeleccionado.value,
            observaciones: observaciones || null
        });
    });

    const datos = {
        condiciones: condiciones
    };


    try {
        const respuesta = await apiFetch(`/salidas/${salidaId}/condicion`, {
            method: "PUT",
            body: JSON.stringify(datos)
        });

        mostrarMensaje(respuesta.mensaje || "Condiciones guardadas correctamente");

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

function formatearNombre(nombre) {
    return nombre
        .replaceAll("_", " ")
        .replace(/\b\w/g, letra => letra.toUpperCase());
}

function mostrarMensaje(texto) {
    mensaje.textContent = texto;

    setTimeout(function () {
        mensaje.textContent = "";
    }, 2000);
}