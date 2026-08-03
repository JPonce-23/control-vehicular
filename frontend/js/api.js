const API_URL = (() => {
    const configurada = String(window.CONTROL_VEHICULAR_API_URL || "").trim();
    if (configurada) return configurada.replace(/\/$/, "");

    if (["localhost", "127.0.0.1"].includes(window.location.hostname)) {
        return "http://127.0.0.1:8000";
    }

    return window.location.origin.replace(/\/$/, "");
})();

function getToken() {
    return localStorage.getItem("token");
}

async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = { ...(options.headers || {}) };

    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    let response;
    try {
        response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    } catch {
        throw new Error("No fue posible conectar con el servidor");
    }

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
        ? await response.json().catch(() => null)
        : await response.text().catch(() => null);

    if (!response.ok) {
        if (response.status === 401 && !endpoint.endsWith("/auth/login")) {
            localStorage.removeItem("token");
        }
        if (Array.isArray(data?.detail)) {
            const errores = data.detail
                .map(error => `${error.loc.join(".")}: ${error.msg}`)
                .join(" | ");
            throw new Error(errores);
        }
        throw new Error(data?.detail || data || "Error en la petición");
    }

    return data;
}

function mostrarMensaje(texto, tipo = "ok") {
    const el = document.getElementById("mensaje");
    if (!el) return;

    if (!texto) {
        el.textContent = "";
        el.className = "message";
        return;
    }

    el.textContent = texto;
    el.className = `message ${tipo} show`;
    setTimeout(() => el.classList.remove("show"), 3500);
}

function recargarConMensaje(texto, tipo = "ok") {
    sessionStorage.setItem("mensajePostRecarga", JSON.stringify({ texto, tipo }));
    window.location.reload();
}

function escaparHTML(valor) {
    return String(valor ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatearFechaSolo(fecha) {
    if (!fecha) return "Sin registro";
    return String(fecha).substring(0, 10);
}

document.addEventListener("DOMContentLoaded", () => {
    const pendiente = sessionStorage.getItem("mensajePostRecarga");
    if (!pendiente) return;
    sessionStorage.removeItem("mensajePostRecarga");
    try {
        const { texto, tipo } = JSON.parse(pendiente);
        mostrarMensaje(texto, tipo);
    } catch {
        // No bloquear la página si el almacenamiento contiene un valor inválido.
    }
});
