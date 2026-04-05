import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

type Property = {
  id: number;
  title: string;
  rent: number;
  location: string;
  description: string;
  available: boolean;
  is_verified: boolean;
  recommendation_score?: number;
  housing_meta?: Record<string, unknown>;
};

export default function Listings() {
  const { user } = useAuth();
  const [items, setItems] = useState<Property[]>([]);
  const [meta, setMeta] = useState<{
    page: number;
    pages: number;
    total: number;
    region_filter?: string | null;
  } | null>(null);
  const [page, setPage] = useState(1);
  const [hint, setHint] = useState("");

  const role = user?.role || "tenant";
  const useRecommended = user && (role === "tenant" || role === "admin");

  useEffect(() => {
    setHint("");
    const params = { page, per_page: 8 };
    if (useRecommended) {
      api
        .get<{ properties: Property[]; meta: typeof meta }>("/property/recommended", { params })
        .then((r) => {
          setItems(r.data.properties);
          setMeta(r.data.meta);
        })
        .catch((ex) => {
          const status = (ex as { response?: { status?: number } })?.response?.status;
          if (status === 403) {
            setHint("Listing access restricted (trust score). Complete a genuine Lifestyle ML profile.");
            setItems([]);
            setMeta({ page: 1, pages: 0, total: 0 });
            return;
          }
          api
            .get<{ properties: Property[]; meta: typeof meta }>("/property/", { params })
            .then((r) => {
              setItems(r.data.properties);
              setMeta(r.data.meta);
            })
            .catch(() => setItems([]));
        });
    } else {
      api
        .get<{ properties: Property[]; meta: typeof meta }>("/property/", { params })
        .then((r) => {
          setItems(r.data.properties);
          setMeta(r.data.meta);
        })
        .catch(() => setItems([]));
    }
  }, [page, useRecommended]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-3xl font-bold text-white">Listings</h1>
        <p className="mt-2 text-slate-400 max-w-2xl">
          {useRecommended ? (
            <>
              <strong className="text-slate-300">India-only</strong> listings: filtered by the city you pick
              in Lifestyle ML, then ranked by rent vs your budget (same idea as{" "}
              <code className="text-livora-300/90">refined_housing_engine</code> in{" "}
              <code className="text-slate-500">roomate.ipynb</code>). Owners should fill{" "}
              <strong className="text-slate-300">housing_meta</strong> (area, bedrooms, bathrooms) for
              better ranking.
            </>
          ) : (
            "Browse India listings. Tenants who complete Lifestyle ML see the same feed ordered for their city and budget."
          )}
        </p>
        {meta?.region_filter && (
          <p className="mt-2 text-sm text-livora-400">Region filter: {meta.region_filter}</p>
        )}
        {hint && (
          <p className="mt-2 rounded-lg bg-amber-500/10 border border-amber-500/30 px-3 py-2 text-sm text-amber-200">
            {hint}
          </p>
        )}
      </div>
      <div className="grid sm:grid-cols-2 gap-6">
        {items.map((p) => (
          <article key={p.id} className="glass rounded-2xl overflow-hidden flex flex-col">
            <div className="h-32 bg-gradient-to-br from-livora-900/40 to-slate-900 flex items-center justify-center text-livora-500/40 text-4xl font-display">
              ◎
            </div>
            <div className="p-5 flex-1 flex flex-col">
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-semibold text-white">{p.title}</h2>
                {p.is_verified && (
                  <span className="text-[10px] uppercase tracking-wider text-livora-400 shrink-0">
                    Verified
                  </span>
                )}
              </div>
              {p.recommendation_score != null && (
                <p className="text-xs text-livora-400/90 mt-1">
                  Match score {(p.recommendation_score * 100).toFixed(1)}%
                </p>
              )}
              <p className="text-livora-400 font-semibold mt-2">₹{p.rent.toLocaleString()}/mo</p>
              <p className="text-sm text-slate-500 mt-1">{p.location}</p>
              <p className="text-sm text-slate-400 mt-3 line-clamp-2 flex-1">{p.description}</p>
              <p className="text-xs text-slate-600 mt-3">
                {p.available ? "Available" : "Unavailable"}
              </p>
            </div>
          </article>
        ))}
      </div>
      {meta && meta.pages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            type="button"
            className="btn-secondary text-sm py-2"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </button>
          <span className="px-4 py-2 text-sm text-slate-400">
            Page {meta.page} / {meta.pages}
          </span>
          <button
            type="button"
            className="btn-secondary text-sm py-2"
            disabled={page >= meta.pages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      )}
      {!user && (
        <p className="text-center text-slate-500 text-sm">
          <Link to="/login" className="text-livora-400 hover:underline">
            Log in as a tenant
          </Link>{" "}
          for region-based recommended listings.
        </p>
      )}
    </div>
  );
}
