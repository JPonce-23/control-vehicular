const tablaPersonas = document.getElementById("tablaPersonas");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", cargarPersonas);

async function cargarPersonas() { 
    try {
        const personas = await apiFetch("/personas/");

        tablaPersonas.innerHTML = "";

        personas.forEach(persona => {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${persona.id}</td>
                <td>${persona.nombre}</td>
                <td>${persona.apellido_paterno}</td>
                <td>${persona.apellido_materno || ""}</td>
                <td>${persona.rfc || ""}</td>
                <td>${persona.num_licencia || ""}</td>
                <td>${persona.tipo_licencia}</td>
                <td>${persona.vigencia_licencia}</td>
                <td>${persona.estado}</td>
            `;

            tablaPersonas.appendChild(fila);
        });
    } catch (error) {
        mensaje.textContent = error.message;
    }
}