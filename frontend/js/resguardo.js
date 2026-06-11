document.addEventListener("DOMContentLoaded", function () {
    const selectSalida = document.getElementById("salida_id");
    const btnPreview = document.getElementById("btnPreview");
    const btnGenerar = document.getElementById("btnGenerar");
    const btnDescargar = document.getElementById("btnDescargar");
    const previewContainer = document.getElementById("previewContainer");
    const mensaje = document.getElementById("mensaje");

    btnPreview.addEventListener("click", mostrarPreview);
    btnGenerar.addEventListener("click", generarResguardo);
    btnDescargar.addEventListener("click", descargarResguardo);

    cargarRegresos();

    async function cargarRegresos() {
        try {
            const regresos = await apiFetch("/regresos/");
            regresos.forEach(function (regreso) {
                const option = document.createElement("option");
                option.value = regreso.salida_id;
                option.textContent = `Salida #${regreso.salida_id} - Regreso #${regreso.id}`;
                selectSalida.appendChild(option);
            });
        } catch (error) {
            mensaje.textContent = error.message;
        }
    }

    async function mostrarPreview() {
        const salidaId = selectSalida.value;
        if (!salidaId) {
            mensaje.textContent = "Selecciona una salida primero";
            return;
        }
        try {
            const preview = await apiFetch(`/salidas/${salidaId}/resguardo-preview`);
            previewContainer.innerHTML = `
                <h3>Vista previa del resguardo</h3>
                <p><strong>Salida ID:</strong> ${salidaId}</p>
                <p><strong>Vehículo:</strong> ${preview.vehiculo?.marca || ""} ${preview.vehiculo?.tipo || ""} ${preview.vehiculo?.modelo_anio || ""}</p>
                <p><strong>Placa:</strong> ${preview.vehiculo?.placa || "Sin dato"}</p>
                <p><strong>Persona:</strong> ${preview.persona?.nombre || ""} ${preview.persona?.apellido_paterno || ""} ${preview.persona?.apellido_materno || ""}</p>
                <p><strong>Kilometraje salida:</strong> ${preview.salida?.km_odometro_salida || "Sin dato"}</p>
                <p><strong>Kilometraje regreso:</strong> ${preview.regreso?.km_odometro_regreso || "Sin dato"}</p>
                <p><strong>Gasolina salida:</strong> ${preview.salida?.nivel_gasolina_salida || "Sin dato"}</p>
                <p><strong>Gasolina regreso:</strong> ${preview.regreso?.nivel_gasolina_regreso || "Sin dato"}</p>
                <p><strong>Finalidad de uso:</strong> ${preview.salida?.finalidad_uso || "Sin dato"}</p>
                <p><strong>Finalidad devolución:</strong> ${preview.regreso?.finalidad_devolucion || "Sin dato"}</p>
            `;
            mensaje.textContent = "";
        } catch (error) {
            mensaje.textContent = error.message;
        }
    }

    async function generarResguardo(event) {
        event.preventDefault();
        const salidaId = selectSalida.value;
        const previewActual = previewContainer.innerHTML;
        if (!salidaId) {
            mensaje.textContent = "Selecciona una salida primero";
            return;
        }
        try {
            await apiFetch(`/salidas/${salidaId}/resguardo`, {
                method: "POST"
            });
            previewContainer.innerHTML = previewActual;
            selectSalida.value = salidaId;
            mostrarMensaje("Resguardo generado correctamente");
        } catch (error) {
            previewContainer.innerHTML = previewActual;
            selectSalida.value = salidaId;
            mensaje.textContent = error.message;
        }
    }

    async function descargarResguardo() {
        const salidaId = selectSalida.value;
        if (!salidaId) {
            mensaje.textContent = "Selecciona una salida primero";
            return;
        }
        try {
            const token = getToken();
            const response = await fetch(`${API_URL}/salidas/${salidaId}/resguardo`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (!response.ok) {
                mensaje.textContent = "No se pudo descargar el resguardo";
                return;
            }
            const archivo = await response.blob();
            const url = window.URL.createObjectURL(archivo);
            const enlace = document.createElement("a");
            enlace.href = url;
            enlace.download = `resguardo_salida_${salidaId}.docx`;
            document.body.appendChild(enlace);
            enlace.click();
            enlace.remove();
            window.URL.revokeObjectURL(url);
            mostrarMensaje("Resguardo descargado correctamente");
        } catch (error) {
            mensaje.textContent = error.message;
        }
    }

    function mostrarMensaje(texto) {
        mensaje.textContent = texto;
        setTimeout(function () {
            mensaje.textContent = "";
        }, 2000);
    }
});