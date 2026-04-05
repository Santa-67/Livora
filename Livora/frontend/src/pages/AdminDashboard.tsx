import { useEffect, useState } from "react";
import { api } from "../api/client";

type U = { id: number; email: string; name: string; role?: string };
type P = { id: number; title: string; location: string; rent: number };

export default function AdminDashboard() {
  const [dash, setDash] = useState<Record<string, number> | null>(null);
  const [users, setUsers] = useState<U[]>([]);
  const [props, setProps] = useState<P[]>([]);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const [d, u, p] = await Promise.all([
        api.get("/admin/dashboard"),
        api.get<{ users: U[] }>("/admin/users?per_page=100"),
        api.get<{ properties: P[] }>("/admin/properties?per_page=100"),
      ]);
      setDash(d.data);
      setUsers(u.data.users);
      setProps(p.data.properties);
    } catch {
      setErr("Failed to load admin data.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function removeUser(id: number) {
    if (!confirm("Delete this user?")) return;
    await api.delete(`/admin/user/${id}/remove`);
    load();
  }

  async function removeProp(id: number) {
    if (!confirm("Delete this property?")) return;
    await api.delete(`/admin/property/${id}`);
    load();
  }

  async function setRole(id: number, role: string) {
    await api.patch(`/admin/user/${id}`, { role });
    load();
  }

  return (
    <div className="space-y-10">
      <h1 className="font-display text-3xl font-bold text-white">Admin</h1>
      {err && <p className="text-rose-300">{err}</p>}
      {dash && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(dash).map(([k, v]) => (
            <div key={k} className="glass rounded-xl p-4">
              <p className="text-xs text-slate-500 uppercase">{k}</p>
              <p className="text-2xl font-display text-livora-400">{v}</p>
            </div>
          ))}
        </div>
      )}

      <section>
        <h2 className="text-lg font-semibold text-white mb-3">Users</h2>
        <div className="overflow-x-auto glass rounded-xl">
          <table className="w-full text-sm text-left">
            <thead className="text-slate-500 border-b border-slate-800">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">Name</th>
                <th className="p-3">Email</th>
                <th className="p-3">Role</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-slate-800/80">
                  <td className="p-3 text-slate-400">{u.id}</td>
                  <td className="p-3 text-white">{u.name}</td>
                  <td className="p-3 text-slate-400">{u.email}</td>
                  <td className="p-3">
                    <select
                      className="input-field text-xs py-1"
                      value={u.role || "tenant"}
                      onChange={(e) => setRole(u.id, e.target.value)}
                    >
                      <option value="tenant">tenant</option>
                      <option value="owner">owner</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td className="p-3">
                    <button
                      type="button"
                      className="text-rose-400 text-xs hover:underline"
                      onClick={() => removeUser(u.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-white mb-3">Properties</h2>
        <div className="overflow-x-auto glass rounded-xl">
          <table className="w-full text-sm text-left">
            <thead className="text-slate-500 border-b border-slate-800">
              <tr>
                <th className="p-3">ID</th>
                <th className="p-3">Title</th>
                <th className="p-3">Location</th>
                <th className="p-3">Rent</th>
                <th className="p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {props.map((p) => (
                <tr key={p.id} className="border-b border-slate-800/80">
                  <td className="p-3 text-slate-400">{p.id}</td>
                  <td className="p-3 text-white">{p.title}</td>
                  <td className="p-3 text-slate-400">{p.location}</td>
                  <td className="p-3 text-slate-400">₹{p.rent}</td>
                  <td className="p-3">
                    <button
                      type="button"
                      className="text-rose-400 text-xs hover:underline"
                      onClick={() => removeProp(p.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
