import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

type PublicUser = {
  id: number;
  name: string;
  bio?: string;
  budget?: number;
  gender?: string;
  move_in_date?: string | null;
  avatar_url?: string;
  is_verified?: boolean;
  created_at?: string;
  lifestyle?: {
    questionnaire?: Record<string, unknown>;
    ml_features?: unknown;
  };
};

type MatchRow = {
  id: number;
  status: string;
  initiator_id?: number | null;
  other_user_id?: number;
};

export default function RoommateDetail() {
  const { userId } = useParams<{ userId: string }>();
  const { user: me } = useAuth();
  const [profile, setProfile] = useState<PublicUser | null>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState("");
  const [matchInfo, setMatchInfo] = useState<MatchRow | null>(null);
  const [canChat, setCanChat] = useState(false);
  const [busy, setBusy] = useState(false);

  const pid = userId ? parseInt(userId, 10) : NaN;

  useEffect(() => {
    if (!userId || Number.isNaN(pid)) return;
    setErr("");
    setLoading(true);
    api
      .get<{ user: PublicUser }>(`/user/${userId}`)
      .then((r) => setProfile(r.data.user))
      .catch(() => setErr("Could not load profile."))
      .finally(() => setLoading(false));
  }, [userId, pid]);

  const refreshMatchState = useCallback(() => {
    if (!me || Number.isNaN(pid) || pid === me.id) return;
    api
      .get<{ matches: MatchRow[] }>("/match/my")
      .then((r) => {
        const found = r.data.matches.find((row) => row.other_user_id === pid);
        setMatchInfo(found || null);
      })
      .catch(() => setMatchInfo(null));
    api
      .get<{ can_chat: boolean }>(`/match/can-chat/${pid}`)
      .then((r) => setCanChat(r.data.can_chat))
      .catch(() => setCanChat(false));
  }, [me, pid]);

  useEffect(() => {
    refreshMatchState();
  }, [refreshMatchState, actionMsg]);

  async function sendRequest() {
    setBusy(true);
    setActionMsg("");
    try {
      await api.post("/match/", { user2_id: pid });
      setActionMsg("Request sent. They’ll see it under their match requests.");
      refreshMatchState();
    } catch (ex: unknown) {
      const m = (ex as { response?: { data?: { error?: string } } })?.response?.data?.error;
      setActionMsg(m || "Could not send request.");
    } finally {
      setBusy(false);
    }
  }

  async function respond(matchId: number, status: "accepted" | "rejected") {
    setBusy(true);
    try {
      await api.patch(`/match/${matchId}`, { status });
      setActionMsg(status === "accepted" ? "You accepted — you can chat now." : "Request declined.");
      refreshMatchState();
    } catch {
      setActionMsg("Could not update request.");
    } finally {
      setBusy(false);
    }
  }

  const q = profile?.lifestyle?.questionnaire;
  const qEntries =
    q && typeof q === "object"
      ? Object.entries(q).filter(([k]) => k !== "ml_features")
      : [];

  const isSelf = me && profile && me.id === profile.id;
  const showTenantActions = me && profile && me.role === "tenant" && !isSelf;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link
        to="/roommates"
        className="inline-flex text-sm text-livora-400 hover:text-livora-300 transition"
      >
        ← Back to compatibility
      </Link>

      {loading && <p className="text-slate-500">Loading…</p>}
      {err && (
        <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-rose-300">
          {err}
        </p>
      )}

      {profile && !loading && (
        <div className="glass rounded-2xl p-8 space-y-6">
          {showTenantActions && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4 space-y-3">
              <h3 className="text-sm font-semibold text-white">Roommate request</h3>
              {actionMsg && <p className="text-sm text-livora-300">{actionMsg}</p>}
              {matchInfo?.status === "pending" && matchInfo.initiator_id === me?.id && (
                <p className="text-sm text-slate-400">Waiting for them to accept.</p>
              )}
              {matchInfo?.status === "pending" && matchInfo.initiator_id !== me?.id && (
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    className="btn-primary text-sm"
                    disabled={busy}
                    onClick={() => respond(matchInfo.id, "accepted")}
                  >
                    Accept request
                  </button>
                  <button
                    type="button"
                    className="btn-secondary text-sm"
                    disabled={busy}
                    onClick={() => respond(matchInfo.id, "rejected")}
                  >
                    Decline
                  </button>
                </div>
              )}
              {(!matchInfo || matchInfo.status === "rejected") && (
                <button type="button" className="btn-primary text-sm" disabled={busy} onClick={sendRequest}>
                  Send roommate request
                </button>
              )}
              {canChat && (
                <Link
                  to={`/messages/${pid}`}
                  className="inline-flex btn-primary text-sm no-underline"
                >
                  Open chat
                </Link>
              )}
            </div>
          )}

          <div className="flex flex-col sm:flex-row sm:items-start gap-4">
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt=""
                className="w-24 h-24 rounded-2xl object-cover border border-slate-700"
              />
            ) : (
              <div className="w-24 h-24 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-2xl text-slate-500 font-display">
                {profile.name?.[0]?.toUpperCase() ?? "?"}
              </div>
            )}
            <div>
              <h1 className="font-display text-3xl font-bold text-white">{profile.name}</h1>
              <div className="mt-2 flex flex-wrap gap-2 text-sm">
                {profile.gender && (
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-300">{profile.gender}</span>
                )}
                {profile.budget != null && (
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-300">
                    Budget ~₹{profile.budget}
                  </span>
                )}
                {profile.is_verified && (
                  <span className="rounded-md bg-livora-500/20 px-2 py-0.5 text-livora-300">Verified</span>
                )}
              </div>
              {profile.move_in_date && (
                <p className="text-sm text-slate-500 mt-2">Move-in: {profile.move_in_date}</p>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">Bio</h2>
            <p className="mt-2 text-slate-200 whitespace-pre-wrap">{profile.bio || "No bio yet."}</p>
          </div>

          {qEntries.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">
                Lifestyle questionnaire
              </h2>
              <dl className="mt-3 grid sm:grid-cols-2 gap-3 text-sm">
                {qEntries.map(([k, v]) => (
                  <div key={k} className="rounded-lg bg-slate-900/50 border border-slate-800 px-3 py-2">
                    <dt className="text-slate-500 capitalize">{k.replace(/_/g, " ")}</dt>
                    <dd className="text-slate-200 mt-0.5">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {qEntries.length === 0 && (
            <p className="text-slate-500 text-sm">
              No lifestyle questionnaire on file. They may not have completed the Lifestyle ML form yet.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
