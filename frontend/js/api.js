const API_URL = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("token");
}

async function apiFetch(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        "Content-Type": "application/json",
        ...options.headers
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
    if (Array.isArray(data?.detail)) {
        const errores = data.detail.map(error => {
            return `${error.loc.join(".")}: ${error.msg}`;
        }).join(" | ");

        throw new Error(errores);
    }

    throw new Error(data?.detail || "Error en la petición");
}
    return data;
}