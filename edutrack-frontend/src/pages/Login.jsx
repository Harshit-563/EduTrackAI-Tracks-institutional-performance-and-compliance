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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-primary rounded-lg mb-4 mx-auto">
            <span className="text-xl font-bold text-white">⚡</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">EduTrack</h1>
          <p className="text-slate-400">Institutional Evaluation System</p>
        </div>

        {/* Login Form */}
        <form onSubmit={onSubmit} className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-8">
          <h2 className="text-xl font-bold text-white mb-2">Sign In</h2>
          <p className="text-sm text-slate-400 mb-6">Use demo credentials below or connect to backend</p>

          {/* Email */}
          <div className="mb-5">
            <label className="block text-sm font-semibold text-slate-300 mb-2">Email Address</label>
            <input 
              type="email"
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20 transition"
              placeholder="user@example.com"
            />
          </div>

          {/* Password */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-300 mb-2">Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              className="w-full px-4 py-2.5 bg-slate-700/40 border border-slate-600/40 rounded-lg text-white text-sm focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20 transition"
              placeholder="••••••••"
            />
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button 
            type="submit" 
            disabled={loading} 
            className="w-full py-2.5 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 disabled:opacity-60 text-white font-semibold rounded-lg transition mb-4"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          {/* Demo Info */}
          <div className="p-4 bg-slate-700/20 border border-slate-600/30 rounded-lg text-xs">
            <p className="text-slate-400 mb-2"><strong>📝 Demo Credentials:</strong></p>
            <p className="text-slate-500 font-mono">user@example.com / password123</p>
          </div>
        </form>

        {/* Footer */}
        <p className="text-center text-slate-500 text-xs mt-6">
          Protected by secure authentication
        </p>
      </div>
    </div>
  );
}
