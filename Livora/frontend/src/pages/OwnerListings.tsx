import { useEffect, useState } from "react";
import { api } from "../api/client";

type Property = {
  id: number;
  title: string;
  rent: number;
  location: string;
  description: string;
  available: boolean;
  housing_meta?: Record<string, unknown>;
};

export default function OwnerListings() {
  const [mine, setMine] = useState<Property[]>([]);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    rent: 15000,
    location: "",
    area: 4000,
    bedrooms: 3,
    bathrooms: 2,
    furnishing: 1,
    region: "mumbai",
  });

  function load() {
    api.get<{ properties: Property[] }>("/property/mine").then((r) => setMine(r.data.properties));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setMsg("");
    setLoading(true);
    try {
      await api.post("/property/", {
        title: form.title,
        description: form.description,
        rent: form.rent,
        location: form.location,
        available: true,
        housing_meta: {
          area: form.area,
          bedrooms: form.bedrooms,
          bathrooms: form.bathrooms,
          furnishing: form.furnishing,
          region: form.region.replace(/\s+/g, "_"),
        },
      });
      setMsg("Property created.");
      setForm((f) => ({
        ...f,
        title: "",
        description: "",
      }));
      load();
    } catch (ex: unknown) {
      const d = (ex as {
        response?: { data?: { error?: string; messages?: Record<string, unknown> } };
      })?.response?.data;
      const msgs = d?.messages;
      const hint =
        msgs && typeof msgs === "object"
          ? " " +
            Object.entries(msgs)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : String(v)}`)
              .join("; ")
          : "";
      setErr((d?.error || "Could not create listing.") + hint);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-10 max-w-4xl mx-auto">
      <div>
        <h1 className="font-display text-3xl font-bold text-white">Owner dashboard</h1>
        <p className="mt-2 text-slate-400">
          Listings are <strong className="text-slate-300">India-only</strong>. Use a clear area string and a
          region slug that matches the city tenants select in Lifestyle ML (e.g.{" "}
          <code className="text-livora-300/90">mumbai</code>,{" "}
          <code className="text-livora-300/90">bangalore</code>). Housing attributes improve ranking vs tenant
          budget (same idea as <code className="text-slate-500">roomate.ipynb</code>).
        </p>
      </div>

      <form onSubmit={submit} className="glass rounded-2xl p-8 space-y-4">
        <h2 className="text-lg font-semibold text-white">New listing</h2>
        <input
          className="input-field"
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          required
          minLength={3}
        />
        <textarea
          className="input-field min-h-[100px]"
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          required
          minLength={10}
        />
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-500">Rent (₹/mo)</label>
            <input
              type="number"
              className="input-field"
              value={form.rent}
              onChange={(e) => setForm((f) => ({ ...f, rent: e.target.valueAsNumber }))}
              min={1000}
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">
              Location (Indian city & area, e.g. Koramangala, Bengaluru)
            </label>
            <input
              className="input-field"
              value={form.location}
              onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
              required
            />
          </div>
        </div>
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-xs text-slate-500">Area (sq ft)</label>
            <input
              type="number"
              className="input-field"
              value={form.area}
              onChange={(e) => setForm((f) => ({ ...f, area: e.target.valueAsNumber }))}
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">Bedrooms</label>
            <input
              type="number"
              className="input-field"
              value={form.bedrooms}
              onChange={(e) => setForm((f) => ({ ...f, bedrooms: e.target.valueAsNumber }))}
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">Bathrooms</label>
            <input
              type="number"
              className="input-field"
              value={form.bathrooms}
              onChange={(e) => setForm((f) => ({ ...f, bathrooms: e.target.valueAsNumber }))}
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">Furnishing (0–2)</label>
            <input
              type="number"
              className="input-field"
              value={form.furnishing}
              min={0}
              max={2}
              onChange={(e) => setForm((f) => ({ ...f, furnishing: e.target.valueAsNumber }))}
            />
          </div>
        </div>
        <div>
          <label className="text-xs text-slate-500">
            Region slug (match Lifestyle ML city: mumbai, delhi, bangalore, …)
          </label>
          <input
            className="input-field"
            value={form.region}
            onChange={(e) => setForm((f) => ({ ...f, region: e.target.value }))}
          />
        </div>
        {err && <p className="text-sm text-rose-300">{err}</p>}
        {msg && <p className="text-sm text-livora-300">{msg}</p>}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Saving…" : "Publish listing"}
        </button>
      </form>

      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Your properties</h2>
        <ul className="space-y-3">
          {mine.map((p) => (
            <li key={p.id} className="glass rounded-xl p-4 flex justify-between gap-4">
              <div>
                <p className="font-medium text-white">{p.title}</p>
                <p className="text-sm text-slate-500">
                  ₹{p.rent.toLocaleString()} · {p.location}
                </p>
              </div>
              <span className="text-xs text-slate-500">{p.available ? "Live" : "Off"}</span>
            </li>
          ))}
        </ul>
        {mine.length === 0 && <p className="text-slate-500 text-sm">No listings yet.</p>}
      </div>
    </div>
  );
}
