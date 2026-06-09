const tablaVehiculos = document.getElementById("tablaVehiculos");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", cargarVehiculos);

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");

        tablaVehiculos.innerHTML = "";

        vehiculos.forEach(vehiculo => {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${vehiculo.id}</td>
                <td>${vehiculo.placa}</td>
                <td>${vehiculo.marca}</td>
                <td>${vehiculo.tipo}</td>
                <td>${vehiculo.modelo_anio}</td>
                <td>${vehiculo.estado}</td>
            `;

            tablaVehiculos.appendChild(fila);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}