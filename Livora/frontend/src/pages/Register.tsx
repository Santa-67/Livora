import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accountType, setAccountType] = useState<"tenant" | "owner">("tenant");
  const [err, setErr] = useState("");
  const { register } = useAuth();
  const nav = useNavigate();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      const u = await register(email, password, name, accountType);
      if (u.role === "owner") nav("/owner");
      else nav("/survey");
    } catch (ex: unknown) {
      const msg =
        (ex as { response?: { data?: { error?: string } } })?.response?.data?.error ||
        "Could not register.";
      setErr(msg);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="glass rounded-2xl p-8">
        <h1 className="font-display text-2xl font-bold text-white">Create account</h1>
        <p className="mt-1 text-sm text-slate-400">
          Join Livora (India) as a tenant looking for flatmates or as a property owner listing homes.
        </p>
        <form onSubmit={submit} className="mt-8 space-y-4">
          {err && (
            <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-3 py-2 text-sm text-rose-300">
              {err}
            </p>
          )}
          <fieldset className="space-y-2">
            <legend className="text-xs font-medium text-slate-400 mb-2">I am registering as</legend>
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
              <input
                type="radio"
                name="acct"
                checked={accountType === "tenant"}
                onChange={() => setAccountType("tenant")}
                className="accent-livora-500"
              />
              Tenant — roommate matching, trust scan, listings in my Indian city
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
              <input
                type="radio"
                name="acct"
                checked={accountType === "owner"}
                onChange={() => setAccountType("owner")}
                className="accent-livora-500"
              />
              Owner — list and manage properties (no roommate ML tools)
            </label>
          </fieldset>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Name</label>
            <input
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={1}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Email</label>
            <input
              className="input-field"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
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
              minLength={8}
            />
          </div>
          <button type="submit" className="btn-primary w-full">
            Sign up
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          Admin accounts are created via{" "}
          <code className="text-slate-400">flask create-admin</code>. Already have an account?{" "}
          <Link to="/login" className="text-livora-400 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
