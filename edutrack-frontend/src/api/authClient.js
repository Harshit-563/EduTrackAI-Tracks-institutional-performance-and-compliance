import client from "./api";

export async function loginRequest(payload) {
  return client.post("/auth/login", payload);
}

export async function meRequest() {
  return client.get("/auth/me");
}
