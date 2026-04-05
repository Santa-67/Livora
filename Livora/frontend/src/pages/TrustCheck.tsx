import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
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
  user: { id: number; name: string; bio?: string; budget?: number; gender?: string };
  compatibility_score: number;
  scoring_method: string;
  clusters: { you: number; them: number } | null;
  trust_scan?: TrustScan;
};

type CachePayload = { matches: MatchRow[]; cachedAt: number };

export default function TrustCheck() {
  const location = useLocation();
  const [health, setHealth] = useState<{
    roommate_model: boolean;
    fake_profile_model: boolean;
    fake_suspicious_threshold?: number;
  } | null>(null);
  const [result, setResult] = useState<{
    fake_probability: number;
    is_suspicious: boolean;
    predicted_class?: number;
    suspicious_threshold?: number;
  } | null>(null);
  const [cached, setCached] = useState<CachePayload | null>(null);
  const [cacheErr, setCacheErr] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMatches, setLoadingMatches] = useState(false);

  useEffect(() => {
    api.get("/ml/health-models").then((r) => setHealth(r.data));
  }, []);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(MATCH_CACHE_KEY);
      if (!raw) {
        setCached(null);
        return;
      }
      const parsed = JSON.parse(raw) as CachePayload;
      if (parsed?.matches && Array.isArray(parsed.matches)) {
        setCached(parsed);
      }
    } catch {
      setCached(null);
    }
  }, [location.pathname]);

  async function runSelf() {
    setErr("");
    setResult(null);
    setLoading(true);
    try {
      const { data } = await api.post<{
        fake_probability: number;
        is_suspicious: boolean;
        predicted_class?: number;
        suspicious_threshold?: number;
      }>("/ml/fake-profile", {});
      setResult(data);
    } catch (ex: unknown) {
      const d = (ex as { response?: { data?: { error?: string } } })?.response?.data;
      setErr(
        d?.error ||
          "Run failed. Save lifestyle data first (Lifestyle ML page) and ensure fake_profile_detector.joblib is in backend/ml/."
      );
    } finally {
      setLoading(false);
    }
  }

  async function refreshMatchesFromServer() {
    setCacheErr("");
    setLoadingMatches(true);
    try {
      const { data } = await api.post<{ matches: MatchRow[] }>("/match/ai", {});
      const payload: CachePayload = { matches: data.matches, cachedAt: Date.now() };
      sessionStorage.setItem(MATCH_CACHE_KEY, JSON.stringify(payload));
      setCached(payload);
    } catch {
      setCacheErr("Could not load compatibility matches. Are you logged in?");
    } finally {
      setLoadingMatches(false);
    }
  }

  const threshold = health?.fake_suspicious_threshold ?? result?.suspicious_threshold ?? 0.85;
  const pct = result ? Math.round((result.fake_probability || 0) * 100) : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-10">
      <div>
        <h1 className="font-display text-3xl font-bold text-white">Trust scan</h1>
        <p className="mt-2 text-slate-400">
          Uses your saved <code className="text-livora-300">ml_features</code> with the trained
          outlier / fake-profile classifier. Profiles are flagged as suspicious only when fake
          probability is <strong className="text-slate-300">≥ {(threshold * 100).toFixed(0)}%</strong>{" "}
          (same rule as compatibility cards).
        </p>
      </div>

      {health && (
        <p className="text-sm text-slate-500">
          Fake model status:{" "}
          <strong className={health.fake_profile_model ? "text-livora-400" : "text-rose-400"}>
            {health.fake_profile_model ? "ready" : "not loaded"}
          </strong>
        </p>
      )}

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white">Your profile</h2>
        <button type="button" className="btn-primary" onClick={runSelf} disabled={loading}>
          {loading ? "Analyzing…" : "Run fake-profile check on my profile"}
        </button>

        {err && (
          <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-sm text-rose-300">
            {err}
          </p>
        )}

        {result && (
          <div className="glass rounded-2xl p-8 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Suspicion score</span>
              <span className="font-display text-3xl font-bold text-white">{pct}%</span>
            </div>
            <div className="h-3 rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${result.is_suspicious ? "bg-rose-500" : "bg-livora-500"}`}
                style={{ width: `${Math.min(100, pct)}%` }}
              />
            </div>
            <p className={`text-lg font-medium ${result.is_suspicious ? "text-rose-300" : "text-livora-300"}`}>
              {result.is_suspicious
                ? `Flagged as suspicious (≥ ${(threshold * 100).toFixed(0)}%) — review before meeting.`
                : "Below suspicion threshold — profile looks consistent with normal patterns."}
            </p>
            {result.predicted_class != null && (
              <p className="text-xs text-slate-500">Raw class: {result.predicted_class}</p>
            )}
          </div>
        )}
      </section>

      <section className="space-y-4 border-t border-slate-800 pt-10">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Compatibility list</h2>
            <p className="mt-1 text-sm text-slate-500 max-w-xl">
              Same trust scores as on the{" "}
              <Link to="/roommates" className="text-livora-400 hover:underline">
                Match
              </Link>{" "}
              page. Data is filled when you run <strong className="text-slate-400">Run AI match</strong>, or
              refresh below.
            </p>
          </div>
          <button
            type="button"
            className="btn-secondary shrink-0"
            onClick={refreshMatchesFromServer}
            disabled={loadingMatches}
          >
            {loadingMatches ? "Loading…" : "Refresh from server"}
          </button>
        </div>

        {cacheErr && (
          <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-sm text-rose-300">
            {cacheErr}
          </p>
        )}

        {!cached?.matches?.length && !loadingMatches && (
          <p className="text-slate-500 text-sm">
            No cached match list yet. Open{" "}
            <Link to="/roommates" className="text-livora-400 hover:underline">
              Match
            </Link>{" "}
            and click <strong className="text-slate-400">Run AI match</strong>, or use{" "}
            <strong className="text-slate-400">Refresh from server</strong> above.
          </p>
        )}

        {cached && cached.matches.length > 0 && (
          <ul className="space-y-3">
            {cached.matches.map((m) => (
              <li
                key={m.user.id}
                className="glass rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div>
                  <Link
                    to={`/roommates/${m.user.id}`}
                    className="font-medium text-white hover:text-livora-300 transition"
                  >
                    {m.user.name}
                  </Link>
                  <p className="text-xs text-slate-500 mt-1">
                    Compatibility {(m.compatibility_score * 100).toFixed(0)}% ·{" "}
                    {m.scoring_method === "ml" && m.clusters
                      ? `you #${m.clusters.you} · them #${m.clusters.them}`
                      : m.scoring_method}
                  </p>
                </div>
                <div className="text-right sm:text-left">
                  {m.trust_scan && m.trust_scan.available ? (
                    <>
                      <span
                        className={`text-sm font-medium ${
                          m.trust_scan.is_suspicious ? "text-rose-300" : "text-livora-300"
                        }`}
                      >
                        Trust {Math.round((m.trust_scan.fake_probability ?? 0) * 100)}% —{" "}
                        {m.trust_scan.is_suspicious ? "suspicious" : "OK"}
                      </span>
                      <div className="mt-2 h-1.5 w-full max-w-[200px] sm:ml-auto rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            m.trust_scan.is_suspicious ? "bg-rose-500" : "bg-livora-500"
                          }`}
                          style={{
                            width: `${Math.min(100, Math.round((m.trust_scan.fake_probability ?? 0) * 100))}%`,
                          }}
                        />
                      </div>
                    </>
                  ) : (
                    <span className="text-sm text-slate-500">
                      Trust n/a
                      {m.trust_scan && !m.trust_scan.available ? ` — ${m.trust_scan.error}` : ""}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}

        {cached?.cachedAt && (
          <p className="text-xs text-slate-600">
            Last match snapshot: {new Date(cached.cachedAt).toLocaleString()}
          </p>
        )}
      </section>
    </div>
  );
}
