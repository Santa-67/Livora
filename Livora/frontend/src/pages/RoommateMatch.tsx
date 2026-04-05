import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { MATCH_CACHE_KEY } from "../lib/matchCache";

type TrustScan =
  | {
      available: true;
      fake_probability: number | null;
      predicted_class?: number;
      is_suspicious: boolean;
    }
  | { available: false; error: string };

type MatchRow = {
  user: {
    id: number;
    name: string;
    bio?: string;
    budget?: number;
    gender?: string;
  };
  compatibility_score: number;
  scoring_method: "ml" | "heuristic";
  clusters: { you: number; them: number } | null;
  trust_scan?: TrustScan;
};

export default function RoommateMatch() {
  const [rows, setRows] = useState<MatchRow[] | null>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(MATCH_CACHE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as { matches?: MatchRow[] };
      if (parsed?.matches && Array.isArray(parsed.matches) && parsed.matches.length > 0) {
        setRows(parsed.matches);
      }
    } catch {
      /* ignore */
    }
  }, []);

  async function load() {
    setErr("");
    setLoading(true);
    try {
      const { data } = await api.post<{ matches: MatchRow[] }>("/match/ai", {});
      setRows(data.matches);
      try {
        sessionStorage.setItem(
          MATCH_CACHE_KEY,
          JSON.stringify({ matches: data.matches, cachedAt: Date.now() })
        );
      } catch {
        /* ignore quota */
      }
    } catch {
      setErr("Could not load matches. Are you logged in?");
      setRows(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-white">Compatibility</h1>
          <p className="mt-2 text-slate-400 max-w-xl">
            Tenants across India: scores use your saved ML vector vs each user’s vector when both are rich
            enough and the roommate model is loaded; otherwise you’ll see heuristic scores. Each row
            includes a <strong className="text-slate-300">trust scan</strong> for that person
            (fake-profile model on their saved <code className="text-livora-300/90">ml_features</code>
            ), same signal as the Trust scan page.
          </p>
        </div>
        <button type="button" className="btn-primary shrink-0" onClick={load} disabled={loading}>
          {loading ? "Scoring…" : "Run AI match"}
        </button>
      </div>

      {err && (
        <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-rose-300">
          {err}
        </p>
      )}

      {!rows && !loading && !err && (
        <p className="text-slate-500 text-center py-12">
          Click <strong className="text-slate-300">Run AI match</strong> to load top 10 matches.
        </p>
      )}

      <div className="grid gap-4">
        {rows?.map((m) => (
          <Link
            key={m.user.id}
            to={`/roommates/${m.user.id}`}
            className="glass rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 no-underline text-inherit transition hover:border-livora-500/40 hover:bg-slate-900/30 border border-transparent focus-visible:outline focus-visible:ring-2 focus-visible:ring-livora-500/50 cursor-pointer"
          >
            <div>
              <h3 className="font-semibold text-white text-lg">{m.user.name}</h3>
              <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                {m.user.bio || "No bio yet"}
              </p>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                {m.user.gender && (
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-300">
                    {m.user.gender}
                  </span>
                )}
                {m.user.budget != null && (
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-300">
                    Budget ~₹{m.user.budget}
                  </span>
                )}
                {m.trust_scan && m.trust_scan.available ? (
                  <>
                    <span
                      className={`rounded-md px-2 py-0.5 font-medium ${
                        m.trust_scan.is_suspicious
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                          : "bg-livora-500/15 text-livora-300 border border-livora-500/30"
                      }`}
                    >
                      Trust {Math.round((m.trust_scan.fake_probability ?? 0) * 100)}%
                      {m.trust_scan.is_suspicious ? " · suspicious" : " · OK"}
                    </span>
                    {m.trust_scan.predicted_class != null && (
                      <span className="rounded-md bg-slate-800/80 px-2 py-0.5 text-slate-500">
                        class {m.trust_scan.predicted_class}
                      </span>
                    )}
                  </>
                ) : (
                  <span
                    className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-500"
                    title={
                      m.trust_scan && !m.trust_scan.available
                        ? m.trust_scan.error
                        : "Trust scan unavailable"
                    }
                  >
                    Trust: n/a
                  </span>
                )}
              </div>
              {m.trust_scan && m.trust_scan.available && (
                <div className="mt-3 max-w-md">
                  <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        m.trust_scan.is_suspicious ? "bg-rose-500" : "bg-livora-500"
                      }`}
                      style={{
                        width: `${Math.min(100, Math.round((m.trust_scan.fake_probability ?? 0) * 100))}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="text-right shrink-0">
              <div className="font-display text-4xl font-bold text-livora-400">
                {(m.compatibility_score * 100).toFixed(0)}
                <span className="text-lg text-slate-500">%</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {m.scoring_method === "ml" ? (
                  <span className="text-livora-300">
                    ML clusters
                    {m.clusters && (
                      <> · you #{m.clusters.you} · them #{m.clusters.them}</>
                    )}
                  </span>
                ) : (
                  <span className="text-amber-200/80">Heuristic (add ML data / models)</span>
                )}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
