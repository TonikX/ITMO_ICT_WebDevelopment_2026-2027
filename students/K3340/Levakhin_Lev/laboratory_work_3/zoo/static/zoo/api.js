export function getToken() {
  return sessionStorage.getItem("zoo-token");
}

export function setToken(token) {
  if (token) sessionStorage.setItem("zoo-token", token);
  else sessionStorage.removeItem("zoo-token");
}

export async function api(path, method = "GET", data) {
  const headers = {};
  if (getToken()) headers.Authorization = "Token " + getToken();
  if (data !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch("/api/" + path, {
    method,
    headers,
    body: data === undefined ? undefined : JSON.stringify(data),
  });
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const message = Array.isArray(payload)
      ? payload.join(" · ")
      : Object.values(payload).flat().join(" · ");
    throw new Error(message || "Ошибка запроса");
  }
  return payload;
}
