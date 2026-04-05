import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

type NumField = { name: string; label: string; min: number; max: number; step: number };
type SelField = { name: string; label: string; options: string[] };
type Schema = { numeric: NumField[]; select: SelField[] };

type ProfileRes = {
  user: { lifestyle?: { questionnaire?: Record<string, unknown> } };
};

const DRAFT_KEY = "livora_lifestyle_survey_v1";

function defaultsFromSchema(schema: Schema): Record<string, string | number> {
  const init: Record<string, string | number> = {};
  schema.numeric.forEach((f) => {
    init[f.name] = f.name === "social_habit_score" ? 0.3 : (f.min ?? 0);
  });
  schema.select.forEach((f) => {
    init[f.name] = f.options[0] ?? "";
  });
  return init;
}

export default function LifestyleSurvey() {
  const [schema, setSchema] = useState<Schema | null>(null);
  const [health, setHealth] = useState<{
    roommate_model: boolean;
    fake_profile_model: boolean;
    roommate_feature_count: number;
  } | null>(null);
  const [values, setValues] = useState<Record<string, string | number>>({});
  const [hydrated, setHydrated] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get<Schema>("/ml/questionnaire-schema").then((r) => setSchema(r.data));
    api.get("/ml/health-models").then((r) => setHealth(r.data));
  }, []);

  const defaults = useMemo(() => (schema ? defaultsFromSchema(schema) : null), [schema]);

  useEffect(() => {
    if (!schema || !defaults) return;

    const applyDraft = (raw: string) => {
      try {
        const parsed = JSON.parse(raw) as Record<string, unknown>;
        if (!parsed || typeof parsed !== "object") return false;
        const merged: Record<string, string | number> = { ...defaults };
        for (const [k, v] of Object.entries(parsed)) {
          if (v === undefined || v === null) continue;
          if (typeof v === "number" && Number.isFinite(v)) merged[k] = v;
          else if (typeof v === "string") merged[k] = v;
        }
        setValues(merged);
        setHydrated(true);
        return true;
      } catch {
        return false;
      }
    };

    try {
      const stored = localStorage.getItem(DRAFT_KEY);
      if (stored && applyDraft(stored)) return;
    } catch {
      /* private mode */
    }

    api
      .get<ProfileRes>("/user/profile")
      .then((r) => {
        const q = r.data.user?.lifestyle?.questionnaire;
        const merged = { ...defaults };
        if (q && typeof q === "object") {
          for (const [k, v] of Object.entries(q)) {
            if (v === undefined || v === null) continue;
            if (typeof v === "number" && Number.isFinite(v)) merged[k] = v;
            else if (typeof v === "string") merged[k] = v;
            else merged[k] = String(v);
          }
        }
        setValues(merged);
        setHydrated(true);
      })
      .catch(() => {
        setValues(defaults);
        setHydrated(true);
      });
  }, [schema, defaults]);

  useEffect(() => {
    if (!hydrated || Object.keys(values).length === 0) return;
    const t = window.setTimeout(() => {
      try {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(values));
      } catch {
        /* quota / private mode */
      }
    }, 350);
    return () => window.clearTimeout(t);
  }, [values, hydrated]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setMsg("");
    setLoading(true);
    const payload: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(values)) {
      if (v === "" || v == null) continue;
      if (typeof v === "number" && Number.isFinite(v)) payload[k] = v;
      else if (typeof v === "string") {
        const n = Number(v);
        payload[k] = v.trim() !== "" && Number.isFinite(n) && /^-?\d/.test(v.trim()) ? n : v;
      }
    }
    try {
      const { data } = await api.post<{ msg: string; features_nonzero: number; features_total: number }>(
        "/ml/apply-questionnaire",
        payload
      );
      setMsg(
        `${data.msg} — ${data.features_nonzero} / ${data.features_total} features non-zero.`
      );
      try {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(values));
      } catch {
        /* ignore */
      }
    } catch (ex: unknown) {
      const d = (ex as { response?: { data?: { error?: string } } })?.response?.data;
      setErr(d?.error || "Failed to save. Is roommate_compatibility_model.joblib in backend/ml/?");
    } finally {
      setLoading(false);
    }
  }

  if (!schema || !hydrated) {
    return <div className="text-slate-400">Loading form…</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-3xl font-bold text-white">Lifestyle & ML vector</h1>
        <p className="mt-2 text-slate-400">
          Answers are mapped to your trained model’s column names. Place both{" "}
          <code className="text-livora-300">.joblib</code> files in{" "}
          <code className="text-livora-300">Livora/backend/ml/</code> then restart the API. Your
          answers are kept in this browser until you clear site data.
        </p>
        {health && (
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <span
              className={`rounded-full px-3 py-1 ${health.roommate_model ? "bg-livora-500/20 text-livora-300" : "bg-rose-500/20 text-rose-300"}`}
            >
              Roommate model: {health.roommate_model ? "loaded" : "missing"}
            </span>
            <span
              className={`rounded-full px-3 py-1 ${health.fake_profile_model ? "bg-livora-500/20 text-livora-300" : "bg-rose-500/20 text-rose-300"}`}
            >
              Fake detector: {health.fake_profile_model ? "loaded" : "missing"}
            </span>
            {health.roommate_feature_count > 0 && (
              <span className="rounded-full bg-slate-700 px-3 py-1 text-slate-300">
                {health.roommate_feature_count} columns expected
              </span>
            )}
          </div>
        )}
      </div>

      <form onSubmit={submit} className="glass rounded-2xl p-8 space-y-6">
        <h2 className="text-lg font-semibold text-white">Numbers</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {schema.numeric.map((f) => (
            <div key={f.name}>
              <label className="block text-xs text-slate-400 mb-1">{f.label}</label>
              <input
                type="number"
                className="input-field"
                min={f.min}
                max={f.max}
                step={f.step}
                value={values[f.name] ?? ""}
                onChange={(e) =>
                  setValues((v) => ({ ...v, [f.name]: e.target.valueAsNumber }))
                }
              />
            </div>
          ))}
        </div>

        <h2 className="text-lg font-semibold text-white pt-2">Categories</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {schema.select.map((f) => (
            <div key={f.name}>
              <label className="block text-xs text-slate-400 mb-1">{f.label}</label>
              <select
                className="input-field"
                value={String(values[f.name] ?? "")}
                onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
              >
                {f.options.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>

        {err && (
          <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-3 py-2 text-sm text-rose-300">
            {err}
          </p>
        )}
        {msg && (
          <p className="rounded-lg bg-livora-500/10 border border-livora-500/30 px-3 py-2 text-sm text-livora-200">
            {msg}
          </p>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full sm:w-auto">
          {loading ? "Saving…" : "Save for ML matching"}
        </button>
      </form>
    </div>
  );
}
