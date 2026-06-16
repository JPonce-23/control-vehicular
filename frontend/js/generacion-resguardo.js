    document.addEventListener("DOMContentLoaded", function () {

        // ── Referencias ──────────────────────────────────────────
        const selectSalida          = document.getElementById("salida_id");
        const condicionesContainer  = document.getElementById("condicionesContainer");
        const inventarioContainer   = document.getElementById("inventarioContainer");
        const previewContainer      = document.getElementById("previewContainer");

        const btnGuardarCondiciones = document.getElementById("btnGuardarCondiciones");
        const btnGuardarInventario  = document.getElementById("btnGuardarInventario");
        const btnPreview            = document.getElementById("btnPreview");
        const btnGenerar            = document.getElementById("btnGenerar");
        const btnDescargar          = document.getElementById("btnDescargar");

        const mensajeSalida         = document.getElementById("mensajeSalida");
        const mensajeCondiciones    = document.getElementById("mensajeCondiciones");
        const mensajeInventario     = document.getElementById("mensajeInventario");
        const mensajeResguardo      = document.getElementById("mensajeResguardo");

        const avisoCondiciones      = document.getElementById("avisoCondiciones");
        const avisoInventario       = document.getElementById("avisoInventario");
        const avisoResguardo        = document.getElementById("avisoResguardo");

        // Estado de pasos
        let condicionesGuardadas = false;
        let inventarioGuardado   = false;
        let resguardoGenerado    = false;

        // ── Inicialización ───────────────────────────────────────
        cargarRegresos();

        selectSalida.addEventListener("change", onSalidaChange);
        btnGuardarCondiciones.addEventListener("click", guardarCondiciones);
        btnGuardarInventario.addEventListener("click", guardarInventario);
        btnPreview.addEventListener("click", mostrarPreview);
        btnGenerar.addEventListener("click", generarResguardo);
        btnDescargar.addEventListener("click", descargarResguardo);

        // ── Cargar salidas con regreso ───────────────────────────
        async function cargarRegresos() {
            try {
                const regresos = await apiFetch("/regresos/");
                regresos.forEach(function (regreso) {
                    const option = document.createElement("option");
                    option.value = regreso.salida_id;
                    option.textContent = `Salida #${regreso.salida_id} — Regreso #${regreso.id}`;
                    selectSalida.appendChild(option);
                });
            } catch (error) {
                mostrarMsg(mensajeSalida, error.message, "error");
            }
        }

        // ── Cambio de salida ─────────────────────────────────────
        async function onSalidaChange() {
            // Resetear estado
            condicionesGuardadas = false;
            inventarioGuardado   = false;
            resguardoGenerado    = false;
            previewContainer.style.display = "none";
            previewContainer.innerHTML = "";
            actualizarProgreso();

            const salidaId = selectSalida.value;
            if (!salidaId) return;

            actualizarProgreso(1);
            await Promise.all([
                cargarCondiciones(salidaId),
                cargarInventario(salidaId)
            ]);
        }

        // ── Cargar condiciones ───────────────────────────────────
        async function cargarCondiciones(salidaId) {
            try {
                const condiciones = await apiFetch(`/salidas/${salidaId}/condicion`);
                condicionesContainer.innerHTML = "";
                avisoCondiciones.style.display = "none";

                condiciones.forEach(function (condicion) {
                    const div = document.createElement("div");
                    div.classList.add("condicion-item");
                    div.dataset.itemId = condicion.item_condicion_id;

                    div.innerHTML = `
                        <p>${formatearNombre(condicion.nombre)}</p>
                        <div class="radio-grupo">
                            <label><input type="radio" name="condicion_${condicion.item_condicion_id}" value="bueno" ${condicion.estado === "bueno" ? "checked" : ""}> B</label>
                            <label><input type="radio" name="condicion_${condicion.item_condicion_id}" value="regular" ${condicion.estado === "regular" ? "checked" : ""}> R</label>
                            <label><input type="radio" name="condicion_${condicion.item_condicion_id}" value="malo" ${condicion.estado === "malo" ? "checked" : ""}> M</label>
                        </div>
                        <input type="text" class="observacion-input observacion-condicion" placeholder="Observaciones (opcional)" value="${condicion.observaciones || ""}">
                    `;
                    condicionesContainer.appendChild(div);
                });

                btnGuardarCondiciones.disabled = false;
                document.getElementById("badge2").classList.remove("bloqueado");
                document.getElementById("badge2").classList.add("completado");

            } catch (error) {
                mostrarMsg(mensajeCondiciones, error.message, "error");
            }
        }

        // ── Cargar inventario ────────────────────────────────────
        async function cargarInventario(salidaId) {
            try {
                const inventario = await apiFetch(`/salidas/${salidaId}/inventario`);
                inventarioContainer.innerHTML = "";

                inventario.forEach(function (item) {
                    const div = document.createElement("div");
                    div.classList.add("inventario-item");
                    div.dataset.itemId = item.item_id;

                    div.innerHTML = `
                        <p>${formatearNombre(item.nombre)} ${item.categoria ? `<small style="font-weight:normal">(${formatearNombre(item.categoria)})</small>` : ""}</p>
                        <div class="radio-grupo">
                            <label><input type="radio" name="inventario_${item.item_id}" value="correcto" ${item.estado === "correcto" ? "checked" : ""}> Correcto</label>
                            <label><input type="radio" name="inventario_${item.item_id}" value="na" ${item.estado === "na" ? "checked" : ""}> N/A</label>
                            <label><input type="radio" name="inventario_${item.item_id}" value="vacio" ${item.estado === "vacio" ? "checked" : ""}> Vacío</label>
                        </div>
                        <input type="text" class="observacion-input observacion-inventario" placeholder="Observaciones (opcional)" value="${item.observaciones || ""}">
                    `;
                    inventarioContainer.appendChild(div);
                });

            } catch (error) {
                mostrarMsg(mensajeInventario, error.message, "error");
            }
        }

        // ── Guardar condiciones ──────────────────────────────────
        async function guardarCondiciones() {
            const salidaId = selectSalida.value;
            if (!salidaId) return;

            const items = document.querySelectorAll(".condicion-item");
            const condiciones = [];

            let valido = true;
            items.forEach(function (item) {
                const itemCondicionId = Number(item.dataset.itemId);
                const radioSeleccionado = item.querySelector(`input[name="condicion_${itemCondicionId}"]:checked`);
                if (!radioSeleccionado) { valido = false; return; }
                const observaciones = item.querySelector(".observacion-condicion").value;
                condiciones.push({
                    item_condicion_id: itemCondicionId,
                    estado: radioSeleccionado.value,
                    observaciones: observaciones || null
                });
            });

            if (!valido) {
                mostrarMsg(mensajeCondiciones, "Selecciona un estado para cada condición.", "error");
                return;
            }

            try {
                const respuesta = await apiFetch(`/salidas/${salidaId}/condicion`, {
                    method: "PUT",
                    body: JSON.stringify({ condiciones })
                });
                condicionesGuardadas = true;
                actualizarProgreso();
                mostrarMsg(mensajeCondiciones, respuesta.mensaje || "Condiciones guardadas correctamente.", "ok");
            } catch (error) {
                mostrarMsg(mensajeCondiciones, error.message, "error");
            }
        }

        // ── Guardar inventario ───────────────────────────────────
        async function guardarInventario() {
            const salidaId = selectSalida.value;
            if (!salidaId) return;

            const items = document.querySelectorAll(".inventario-item");
            const inventario = [];

            let valido = true;
            items.forEach(function (item) {
                const itemId = Number(item.dataset.itemId);
                const radioSeleccionado = item.querySelector(`input[name="inventario_${itemId}"]:checked`);
                if (!radioSeleccionado) { valido = false; return; }
                const observaciones = item.querySelector(".observacion-inventario").value;
                inventario.push({
                    item_id: itemId,
                    estado: radioSeleccionado.value,
                    observaciones: observaciones || null
                });
            });

            if (!valido) {
                mostrarMsg(mensajeInventario, "Selecciona un estado para cada ítem.", "error");
                return;
            }

            try {
                const respuesta = await apiFetch(`/salidas/${salidaId}/inventario`, {
                    method: "PUT",
                    body: JSON.stringify({ inventario })
                });
                inventarioGuardado = true;
                actualizarProgreso();
                mostrarMsg(mensajeInventario, respuesta.mensaje || "Inventario guardado correctamente.", "ok");
            } catch (error) {
                mostrarMsg(mensajeInventario, error.message, "error");
            }
        }

        // ── Vista previa ─────────────────────────────────────────
        async function mostrarPreview() {
            const salidaId = selectSalida.value;
            if (!salidaId) return;

            try {
                const preview = await apiFetch(`/salidas/${salidaId}/resguardo-preview`);
                const condiciones = await apiFetch(`/salidas/${salidaId}/condicion`);
                const inventario  = await apiFetch(`/salidas/${salidaId}/inventario`);

                const fecha = new Date();
                const dia   = String(fecha.getDate()).padStart(2, "0");
                const mes   = String(fecha.getMonth() + 1).padStart(2, "0");
                const anio  = fecha.getFullYear();

                // Mapas para condiciones e inventario
                const condMap = {};
                condiciones.forEach(c => {
                    condMap[c.nombre] = c.estado;
                });

                const invMap = {};
                inventario.forEach(i => {
                    invMap[i.nombre] = i.estado;
                });

                function estadoLetra(e) {
                    if (e === "bueno")   return '<span class="estado-B">✓</span>';
                    if (e === "regular") return '<span class="estado-R">✓</span>';
                    if (e === "malo")    return '<span class="estado-M">✓</span>';
                    return "";
                }

                function celdaEstado(nombre, est) {
                    const e = condMap[nombre] || "";
                    return `
                        <td class="check-cell">${e === est ? estadoLetra(e) : ""}</td>
                    `;
                }

                function celdaInv(nombre) {
                    const e = invMap[nombre] || "";
                    return `<td class="check-cell">${e === "correcto" ? "✓" : ""}</td>`;
                }

                function nivelGas(nivel) {
                    const niveles = ["vacio","cuarto","medio","tres_cuartos","lleno"];
                    const labels  = ["0","1/4","1/2","3/4","4/4"];
                    return niveles.map((n, i) =>
                        `<td class="check-cell">${nivel === n ? "✓" : ""}</td>`
                    ).join("");
                }

                function nivelLlanta(nivel) {
                    // Para simplificar, mostramos 4/4 si no hay dato
                    return `<td></td><td></td><td></td><td class="check-cell">✓</td>`;
                }

                const v = preview.vehiculo  || {};
                const p = preview.persona   || {};
                const s = preview.salida    || {};
                const r = preview.regreso   || {};

                previewContainer.style.display = "block";
                previewContainer.innerHTML = `
                <div class="resguardo-doc">
                    <table>
                        <tr>
                            <td colspan="2" class="resguardo-header">
                                JEFATURA DE SERVICIOS GENERALES<br>
                                CONTROL DE ENTREGAS Y DEVOLUCIONES DE PARQUE VEHICULAR
                            </td>
                            <td>
                                <span class="campo-label">FECHA</span><br>
                                <table style="border:none;width:100%">
                                    <tr>
                                        <td style="border:1px solid #333;text-align:center;font-size:11px">DÍA</td>
                                        <td style="border:1px solid #333;text-align:center;font-size:11px">MES</td>
                                        <td style="border:1px solid #333;text-align:center;font-size:11px">AÑO</td>
                                    </tr>
                                    <tr>
                                        <td style="border:1px solid #333;text-align:center">${dia}</td>
                                        <td style="border:1px solid #333;text-align:center">${mes}</td>
                                        <td style="border:1px solid #333;text-align:center">${anio}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Sección I -->
                        <tr><td colspan="3" class="seccion-titulo">I.- DATOS DEL VEHÍCULO</td></tr>
                        <tr>
                            <td colspan="3">
                                <span class="campo-label">MARCA:</span> <span class="campo-valor">${v.marca || ""}</span> &nbsp;
                                <span class="campo-label">TIPO:</span> <span class="campo-valor">${v.tipo || ""}</span> &nbsp;
                                <span class="campo-label">MODELO:</span> <span class="campo-valor">${v.modelo_anio || ""}</span>
                            </td>
                        </tr>
                        <tr>
                            <td><span class="campo-label">No. SERIE:</span> <span class="campo-valor">${v.num_serie || ""}</span></td>
                            <td><span class="campo-label">PLACAS:</span> <span class="campo-valor">${v.placa || ""}</span></td>
                            <td><span class="campo-label">No. ECO:</span> <span class="campo-valor">${v.num_economico || ""}</span></td>
                        </tr>

                        <!-- Sección II -->
                        <tr><td colspan="3" class="seccion-titulo">II.- TIPO DE MOVIMIENTO</td></tr>
                        <tr>
                            <td><span class="campo-label">FINALIDAD DE USO:</span><br><span class="campo-valor">${s.finalidad_uso || ""}</span></td>
                            <td colspan="2"><span class="campo-label">FINALIDAD EN CASO DE DEVOLUCIÓN:</span><br><span class="campo-valor">${r.finalidad_devolucion || ""}</span></td>
                        </tr>

                        <!-- Sección III -->
                        <tr><td colspan="3" class="seccion-titulo">III.- DATOS DEL ASIGNATARIO</td></tr>
                        <tr>
                            <td colspan="2">
                                <span class="campo-label">NOMBRE:</span> <span class="campo-valor">${p.nombre || ""} ${p.apellido_paterno || ""} ${p.apellido_materno || ""}</span><br>
                                <span class="campo-label">CARGO:</span> <span class="campo-valor">${p.cargo || ""}</span><br>
                                <span class="campo-label">No. LICENCIA:</span> <span class="campo-valor">${p.num_licencia || ""}</span> &nbsp;
                                <span class="campo-label">RFC:</span> <span class="campo-valor">${p.rfc || ""}</span>
                            </td>
                            <td>
                                <span class="campo-label">VIGENTE AL:</span> <span class="campo-valor">${p.vigencia_licencia || ""}</span><br>
                                <span class="campo-label">TIPO:</span> <span class="campo-valor">${p.tipo_licencia || ""}</span>
                            </td>
                        </tr>

                        <!-- Sección IV -->
                        <tr><td colspan="3" class="seccion-titulo">IV.- CONDICIONES DE FUNCIONALIDAD</td></tr>
                        <tr>
                            <td></td>
                            <td style="text-align:center"><strong>B</strong></td>
                            <td style="text-align:center"><strong>R</strong></td>
                            <td style="text-align:center"><strong>M</strong></td>
                            <td></td>
                            <td style="text-align:center"><strong>B</strong></td>
                            <td style="text-align:center"><strong>R</strong></td>
                            <td style="text-align:center"><strong>M</strong></td>
                        </tr>
                        ${filaCondicion("carroceria","CARROCERÍA","sistema_electrico","SISTEMA ELÉCTRICO", condMap)}
                        ${filaCondicion("pintura","PINTURA","sistema_encendido","SISTEMA DE ENCENDIDO", condMap)}
                        ${filaCondicion("vestidura","VESTIDURA","sistema_frenos","SISTEMA DE FRENOS", condMap)}
                        ${filaCondicion("direccion","DIRECCIÓN","sistema_suspension","SISTEMA DE SUSPENSIÓN", condMap)}
                        ${filaCondicion("motor","MOTOR","sistema_transmision","SISTEMA DE TRANSMISIÓN", condMap)}

                        <!-- Sección V -->
                        <tr><td colspan="8" class="seccion-titulo">V.- INVENTARIO DEL VEHÍCULO</td></tr>
                        <tr>
                            <td class="campo-label">PIEZA</td>
                            <td class="check-cell campo-label">✓</td>
                            <td class="campo-label">PIEZA</td>
                            <td class="check-cell campo-label">✓</td>
                            <td class="campo-label">PIEZA</td>
                            <td class="check-cell campo-label">✓</td>
                            <td class="campo-label">PIEZA</td>
                            <td class="check-cell campo-label">✓</td>
                        </tr>
                        ${filaInventario4("tapon_gasolina","TAPÓN GAS.","estereo","ESTÉREO","calefaccion","CALEFACCIÓN","aire_acondicionado","AIRE ACOND.", invMap)}
                        ${filaInventario4("tapon_radiador","TAPÓN RADIADOR","radio_am_fm","RADIO AM/FM","cenicero","CENICERO","juego_herramientas","JGO. HERRAMIENTAS", invMap)}
                        ${filaInventario4("tapon_aceite","TAPÓN ACEITE","antena","ANTENA","encendedor","ENCENDEDOR","extinguidor","EXTINGUIDOR", invMap)}
                        ${filaInventario4("tapones_rines","TAPONES RINES","alarma","ALARMA","visera_derecha","VISERA DERECHA","bayoneta_aceite","BAYONETA (ACE.)", invMap)}
                        ${filaInventario4("emblemas","EMBLEMAS","llave_puertas","LLAVE PUERTAS","visera_izquierda","VISERA IZQUIERDA","bateria","BATERÍA", invMap)}
                        ${filaInventario4("parrillas","PARRILLAS","llave_tapon_gasolina","LLAVE TAPÓN GAS","cinturon_seguridad","CINTURÓN SEG.","juego_placas","JGO. PLACAS", invMap)}
                        ${filaInventario4("limpiadores","LIMPIADORES","llave_cajuela","LLAVE CAJUELA","tapetes","TAPETES","tarjeta_circulacion","TARJETA CIRC.", invMap)}
                        ${filaInventario4("espejo_lateral_izquierdo","ESPEJO LAT. IZQ.","llave_guantera","LLAVE GUANTERA","alfombra_cajuela","ALFOMBRA CAJUELA","poliza_seguro","PÓLIZA SEGURO", invMap)}
                        ${filaInventario4("espejo_lateral_derecho","ESPEJO LAT. DER.","llave_encendido","LLAVE ENCENDIDO","llanta_refaccion","LLANTA REFACCIÓN","poliza_servicio","PÓLIZA SERVICIO", invMap)}
                        ${filaInventario4("espejo_retrovisor","ESPEJO RETROVISOR","sistema_alarma","SISTEMA ALARMA","gato","GATO","verificacion","VERIFICACIÓN", invMap)}
                        ${filaInventario4("llantas","LLANTAS","seguro_aletas","SEGURO ALETAS","llave_birlos","LLAVE BIRLOS","revista_vehicular","REVISTA VEHI.", invMap)}
                        ${filaInventario4("claxon","CLAXON","seguro_puertas","SEGURO PUERTAS","defroster","DEFROSTER","reflejantes","REFLEJANTES", invMap)}

                        <!-- Estado llantas / gasolina / odómetro -->
                        <tr>
                            <td colspan="2" class="campo-label">ESTADO DE LLANTAS</td>
                            <td class="check-cell">¼</td><td class="check-cell">1/2</td><td class="check-cell">3/4</td><td class="check-cell">4/4</td>
                            <td class="campo-label">NIVEL GASOLINA</td>
                            <td colspan="5">
                                <table style="border:none;width:100%"><tr>
                                    <td style="text-align:center;font-size:11px">0</td>
                                    <td style="text-align:center;font-size:11px">1/4</td>
                                    <td style="text-align:center;font-size:11px">1/2</td>
                                    <td style="text-align:center;font-size:11px">3/4</td>
                                    <td style="text-align:center;font-size:11px">4/4</td>
                                </tr><tr>
                                    ${nivelGas(s.nivel_gasolina_salida)}
                                </tr></table>
                            </td>
                            <td><span class="campo-label">LECTURA ODÓMETRO:</span><br>${s.km_odometro_salida || ""} km</td>
                        </tr>

                        <!-- Sección VI -->
                        <tr><td colspan="8" class="seccion-titulo">VI.- FIRMAS DE CONOCIMIENTO</td></tr>
                        <tr>
                            <td colspan="4" style="text-align:center;padding:20px">
                                <div style="border-top:1px solid #333;margin-top:30px;padding-top:4px">
                                    ${p.nombre || ""} ${p.apellido_paterno || ""}<br>
                                    <strong>NOMBRE, FIRMA Y CARGO</strong>
                                </div>
                            </td>
                            <td colspan="4" style="text-align:center;padding:20px">
                                <div style="border-top:1px solid #333;margin-top:30px;padding-top:4px">
                                    Jefe de Departamento<br>
                                    <strong>NOMBRE, FIRMA Y CARGO</strong>
                                </div>
                            </td>
                        </tr>
                    </table>
                </div>`;

            } catch (error) {
                mostrarMsg(mensajeResguardo, error.message, "error");
            }
        }

        // ── Generar resguardo Word ───────────────────────────────
        async function generarResguardo(event) {
            event.preventDefault();
            const salidaId = selectSalida.value;
            if (!salidaId) return;
            try {
                await apiFetch(`/salidas/${salidaId}/resguardo`, { method: "POST" });
                resguardoGenerado = true;
                btnDescargar.disabled = false;
                actualizarProgreso();
                mostrarMsg(mensajeResguardo, "Resguardo generado correctamente.", "ok");
            } catch (error) {
                mostrarMsg(mensajeResguardo, error.message, "error");
            }
        }

        // ── Descargar resguardo ──────────────────────────────────
        async function descargarResguardo() {
            const salidaId = selectSalida.value;
            if (!salidaId) return;
            try {
                const token    = getToken();
                const response = await fetch(`${API_URL}/salidas/${salidaId}/resguardo`, {
                    method: "GET",
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (!response.ok) {
                    mostrarMsg(mensajeResguardo, "No se pudo descargar el resguardo.", "error");
                    return;
                }
                const archivo = await response.blob();
                const url     = window.URL.createObjectURL(archivo);
                const enlace  = document.createElement("a");
                enlace.href     = url;
                enlace.download = `resguardo_salida_${salidaId}.docx`;
                document.body.appendChild(enlace);
                enlace.click();
                enlace.remove();
                window.URL.revokeObjectURL(url);
                mostrarMsg(mensajeResguardo, "Resguardo descargado correctamente.", "ok");
            } catch (error) {
                mostrarMsg(mensajeResguardo, error.message, "error");
            }
        }

        // ── Control de progreso ──────────────────────────────────
        function actualizarProgreso(pasoActivo) {
            // Condiciones
            btnGuardarCondiciones.disabled = !selectSalida.value;

            // Inventario: solo si condiciones guardadas
            btnGuardarInventario.disabled = !condicionesGuardadas;
            document.getElementById("avisoInventario").style.display = condicionesGuardadas ? "none" : "block";
            document.getElementById("badge3").className = "paso-badge " + (condicionesGuardadas ? "" : "bloqueado");

            // Paso 4: solo si inventario guardado
            btnPreview.disabled  = !inventarioGuardado;
            btnGenerar.disabled  = !inventarioGuardado;
            btnDescargar.disabled = !resguardoGenerado;
            document.getElementById("avisoResguardo").style.display = inventarioGuardado ? "none" : "block";
            document.getElementById("badge4").className = "paso-badge " + (inventarioGuardado ? "" : "bloqueado");

            // Progreso visual
            document.getElementById("prog1").className = "progreso-paso" + (selectSalida.value ? " listo" : " activo");
            document.getElementById("prog2").className = "progreso-paso" + (condicionesGuardadas ? " listo" : selectSalida.value ? " activo" : "");
            document.getElementById("prog3").className = "progreso-paso" + (inventarioGuardado ? " listo" : condicionesGuardadas ? " activo" : "");
            document.getElementById("prog4").className = "progreso-paso" + (resguardoGenerado ? " listo" : inventarioGuardado ? " activo" : "");
        }

        // ── Helpers ──────────────────────────────────────────────
        function mostrarMsg(el, texto, tipo) {
            el.textContent = texto;
            el.className   = "mensaje " + tipo;
            if (tipo === "ok") {
                setTimeout(() => { el.textContent = ""; el.className = "mensaje"; }, 3000);
            }
        }

        function formatearNombre(nombre) {
            return nombre.replaceAll("_", " ").replace(/\b\w/g, l => l.toUpperCase());
        }

        function filaCondicion(k1, l1, k2, l2, condMap) {
            function celdas(key) {
                const e = condMap[key] || "";
                return `
                    <td class="check-cell">${e === "bueno"   ? '<span class="estado-B">✓</span>' : ""}</td>
                    <td class="check-cell">${e === "regular" ? '<span class="estado-R">✓</span>' : ""}</td>
                    <td class="check-cell">${e === "malo"    ? '<span class="estado-M">✓</span>' : ""}</td>
                `;
            }
            return `<tr><td class="campo-label">${l1}</td>${celdas(k1)}<td class="campo-label">${l2}</td>${celdas(k2)}</tr>`;
        }

        function filaInventario4(k1,l1,k2,l2,k3,l3,k4,l4, invMap) {
            function ch(k) {
                return `<td class="check-cell">${(invMap[k] === "correcto") ? "✓" : ""}</td>`;
            }
            return `<tr>
                <td class="campo-valor">${l1}</td>${ch(k1)}
                <td class="campo-valor">${l2}</td>${ch(k2)}
                <td class="campo-valor">${l3}</td>${ch(k3)}
                <td class="campo-valor">${l4}</td>${ch(k4)}
            </tr>`;
        }

        function nivelGas(nivel) {
            const niveles = ["vacio","cuarto","medio","tres_cuartos","lleno"];
            return niveles.map(n => `<td class="check-cell">${nivel === n ? "✓" : ""}</td>`).join("");
        }

    });
