import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth, effectiveRole } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const { login } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const from = (loc.state as { from?: { pathname: string } })?.from?.pathname || "/";

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      const u = await login(email, password);
      const r = effectiveRole(u);
      if (r === "admin") nav("/admin", { replace: true });
      else if (r === "owner") nav("/owner", { replace: true });
      else nav(from, { replace: true });
    } catch {
      setErr("Invalid email or password.");
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="glass rounded-2xl p-8">
        <h1 className="font-display text-2xl font-bold text-white">Welcome back</h1>
        <p className="mt-1 text-sm text-slate-400">Log in to sync your ML profile.</p>
        <form onSubmit={submit} className="mt-8 space-y-4">
          {err && (
            <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-3 py-2 text-sm text-rose-300">
              {err}
            </p>
          )}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Email</label>
            <input
              className="input-field"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Password</label>
            <input
              className="input-field"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <button type="submit" className="btn-primary w-full">
            Log in
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          No account?{" "}
          <Link to="/register" className="text-livora-400 hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
