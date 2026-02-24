import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { dummyUsers } from "../data/dummyUsers";
import client from "../api/api";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState(dummyUsers[0].email);
  const [password, setPassword] = useState(dummyUsers[0].password);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const from = location.state?.from || "/";

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Prefer backend auth.
      const response = await client.post("/auth/login", { email, password });
      const payload = response?.data || {};
      const user = payload.user;
      const token = payload.token;

      if (!user || !token) {
        throw new Error("Invalid login response");
      }

      localStorage.setItem("edutrack_token", token);
      login({ email: user.email, role: user.role });

      if (user.role === "reviewer") return navigate("/reviewer", { replace: true });
      if (user.role === "admin") return navigate("/admin", { replace: true });
      if (user.role === "institution") return navigate("/institute", { replace: true });

      return navigate(from, { replace: true });
    } catch (apiError) {
      // Fallback to local dummy users for offline frontend development.
      const fallbackUser = dummyUsers.find((u) => u.email === email && u.password === password);

      if (!fallbackUser) {
        setError(apiError?.message || "Invalid credentials.");
        setLoading(false);
        return;
      }

      localStorage.setItem("edutrack_token", "local-dev-token");
      login({ email: fallbackUser.email, role: fallbackUser.role });

      if (fallbackUser.role === "reviewer") return navigate("/reviewer", { replace: true });
      if (fallbackUser.role === "admin") return navigate("/admin", { replace: true });
      if (fallbackUser.role === "institution") return navigate("/institute", { replace: true });

      return navigate(from, { replace: true });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0f1720] text-gray-100 flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-gray-900/30 border border-gray-800 rounded-xl p-6">
        <h1 className="text-xl font-semibold mb-1">Sign In</h1>
        <p className="text-sm text-gray-400 mb-4">Backend auth enabled. Dummy fallback is available for local testing.</p>

        <label className="text-sm">Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full mt-1 mb-3 px-3 py-2 rounded bg-black/20 border border-gray-700" />

        <label className="text-sm">Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full mt-1 mb-4 px-3 py-2 rounded bg-black/20 border border-gray-700" />

        {error && <div className="text-sm text-red-400 mb-3">{error}</div>}

        <button type="submit" disabled={loading} className="w-full py-2 rounded bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60">
          {loading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
