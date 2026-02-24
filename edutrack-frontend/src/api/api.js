export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function normalizeHeaders(headers = {}) {
  const next = { ...headers };
  if (!Object.keys(next).some((k) => k.toLowerCase() === "accept")) {
    next.Accept = "application/json";
  }
  return next;
}

function normalizeBody(body, headers) {
  if (body === undefined || body === null) return body;

  if (body instanceof FormData || typeof body === "string" || body instanceof Blob) {
    return body;
  }

  if (!Object.keys(headers).some((k) => k.toLowerCase() === "content-type")) {
    headers["Content-Type"] = "application/json";
  }
  return JSON.stringify(body);
}

async function request(path, options = {}) {
  const token = localStorage.getItem("edutrack_token");
  const headers = normalizeHeaders(options.headers || {});

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const body = normalizeBody(options.body, headers);

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body,
  });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("edutrack_token");
      localStorage.removeItem("edutrack_user");
    }
    throw new Error((isJson && (data?.detail || data?.message)) || `Request failed: ${res.status}`);
  }

  return { data, status: res.status };
}

const client = {
  get: (path) => request(path, { method: "GET" }),
  post: (path, body, headers = {}) => request(path, { method: "POST", body, headers }),
};

export default client;

