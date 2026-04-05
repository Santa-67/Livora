import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [budget, setBudget] = useState("");
  const [gender, setGender] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setBio(user.bio || "");
      setBudget(user.budget != null ? String(user.budget) : "");
      setGender(user.gender || "");
    }
  }, [user]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    await api.put("/user/profile", {
      name,
      bio,
      budget: budget ? Number(budget) : undefined,
      gender: gender || undefined,
    });
    await refreshUser();
    setMsg("Profile saved.");
  }

  if (!user) return null;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="font-display text-3xl font-bold text-white mb-2">Your profile</h1>
      <p className="text-slate-400 text-sm mb-8">{user.email}</p>
      <form onSubmit={save} className="glass rounded-2xl p-8 space-y-4">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Name</label>
          <input className="input-field" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Bio</label>
          <textarea
            className="input-field min-h-[100px] resize-y"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Budget (₹)</label>
          <input
            type="number"
            className="input-field"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Gender</label>
          <select
            className="input-field"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
          >
            <option value="">—</option>
            <option value="male">male</option>
            <option value="female">female</option>
            <option value="other">other</option>
          </select>
        </div>
        {msg && <p className="text-sm text-livora-400">{msg}</p>}
        <button type="submit" className="btn-primary">
          Save
        </button>
      </form>
    </div>
  );
}
