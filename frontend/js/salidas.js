const salidaForm = document.getElementById("salidaForm");
const selectVehiculo = document.getElementById("vehiculo_id");
const selectPersona = document.getElementById("persona_id");
const mensaje = document.getElementById("mensaje");

document.addEventListener("DOMContentLoaded", function () {
    cargarVehiculos();
    cargarPersonas();
});

salidaForm.addEventListener("submit", registrarSalida);

async function cargarVehiculos() {
    try {
        const vehiculos = await apiFetch("/vehiculos/");
        const disponibles = vehiculos.filter(vehiculo => vehiculo.estado === "disponible");

        disponibles.forEach(vehiculo => {
            const option = document.createElement("option");
            option.value = vehiculo.id;
            option.textContent = `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.tipo}`;
            selectVehiculo.appendChild(option);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function cargarPersonas() {
    try {
        const personas = await apiFetch("/personas/");
        const activas = personas.filter(persona => persona.estado === "activo");

        activas.forEach(persona => {
            const option = document.createElement("option");
            option.value = persona.id;
            option.textContent = `${persona.nombre} ${persona.apellido_paterno} - Licencia ${persona.num_licencia}`;
            selectPersona.appendChild(option);
        });

    } catch (error) {
        mensaje.textContent = error.message;
    }
}

async function registrarSalida(event) {
    event.preventDefault();

    const datosSalida = {
        vehiculo_id: Number(document.getElementById("vehiculo_id").value),
        persona_id: Number(document.getElementById("persona_id").value),
        capturado_por: 1,
        num_oficio: document.getElementById("num_oficio").value,
        num_expediente: document.getElementById("num_expediente").value,
        cargo_en_viaje: document.getElementById("cargo_en_viaje").value,
        area_en_viaje: document.getElementById("area_en_viaje").value,
        tipo_movimiento: document.getElementById("tipo_movimiento").value,
        forma_movimiento: document.getElementById("forma_movimiento").value,
        fecha_fin_provisional: document.getElementById("fecha_fin_provisional").value || null,
        finalidad_uso: document.getElementById("finalidad_uso").value,
        km_odometro_salida: Number(document.getElementById("km_odometro_salida").value),
        nivel_gasolina_salida: document.getElementById("nivel_gasolina_salida").value,
        estado_llantas_salida: document.getElementById("estado_llantas_salida").value,
        observaciones: document.getElementById("observaciones").value,
        observaciones_croquis: document.getElementById("observaciones_croquis").value
    };

    console.log(datosSalida);

    try {
        const salida = await apiFetch("/salidas/", {
            method: "POST",
            body: JSON.stringify(datosSalida)
        });

        mensaje.textContent = "Salida registrada correctamente";
        localStorage.setItem("salida_id_actual", salida.id);

    } catch (error) {
        mensaje.textContent = error.message;
    }
}