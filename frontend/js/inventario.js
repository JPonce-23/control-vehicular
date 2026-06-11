const selectSalida = document.getElementById("salida_id");
const inventarioContainer = document.getElementById("inventarioContainer");
const btnGuardarInventario = document.getElementById("btnGuardarInventario");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    cargarSalidas();
});

selectSalida.addEventListener("change", cargarInventario);
btnGuardarInventario.addEventListener("click", guardarInventario);

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

async function cargarInventario() {
    const salidaId = selectSalida.value;

    if (!salidaId) {
        inventarioContainer.innerHTML = "Selecciona una salida para cargar el inventario.";
        return;
    }

    try {
        const inventario = await apiFetch(`/salidas/${salidaId}/inventario`);

        inventarioContainer.innerHTML = "";

        inventario.forEach(function (item) {
            const div = document.createElement("div");

            div.classList.add("inventario-item");
            div.dataset.itemId = item.item_id;

            div.innerHTML = `
                <p>
                    <strong>${formatearNombre(item.nombre)}</strong>
                    ${item.categoria ? `<small>(${formatearNombre(item.categoria)})</small>` : ""}
                </p>

                <label>
                    <input type="radio" name="inventario_${item.item_id}" value="correcto"
                        ${item.estado === "correcto" ? "checked" : ""}>
                    Correcto
                </label>

                <label>
                    <input type="radio" name="inventario_${item.item_id}" value="na"
                        ${item.estado === "na" ? "checked" : ""}>
                    N/A
                </label>

                <label>
                    <input type="radio" name="inventario_${item.item_id}" value="vacio"
                        ${item.estado === "vacio" ? "checked" : ""}>
                    Vacío
                </label>

                <br>

                <label>Observaciones:</label>
                <input 
                    type="text" 
                    class="observacion-inventario" 
                    value="${item.observaciones || ""}"
                >

                <hr>
            `;

            inventarioContainer.appendChild(div);
        });

        mensaje.textContent = "";

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function guardarInventario() {
    const salidaId = selectSalida.value;

    if (!salidaId) {
        mensaje.textContent = "Selecciona una salida primero";
        return;
    }

    const items = document.querySelectorAll(".inventario-item");

    const inventario = [];

    items.forEach(function (item) {
        const itemId = Number(item.dataset.itemId);

        const radioSeleccionado = item.querySelector(
            `input[name="inventario_${itemId}"]:checked`
        );

        const observaciones = item.querySelector(".observacion-inventario").value;

        inventario.push({
            item_id: itemId,
            estado: radioSeleccionado.value,
            observaciones: observaciones || null
        });
    });

    const datos = {
        inventario: inventario
    };

    try {
        const respuesta = await apiFetch(`/salidas/${salidaId}/inventario`, {
            method: "PUT",
            body: JSON.stringify(datos)
        });

        mostrarMensaje(respuesta.mensaje || "Inventario guardado correctamente");

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