import { useEffect, useState, useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import { io, type Socket } from "socket.io-client";
import { api, apiBaseURL } from "../api/client";
import { useAuth } from "../context/AuthContext";

type Msg = {
  id: number;
  sender_id: number;
  receiver_id: number;
  message: string;
  timestamp: string;
};

type Conversation = {
  peer_id: number;
  peer_name: string;
  last_message: Msg | null;
};

type MatchReq = {
  id: number;
  status: string;
  other_user: { id: number; name: string } | null;
};


export default function MessagesPage() {
  const { userId } = useParams<{ userId?: string }>();
  const { user } = useAuth();
  const me = user?.id;
  const peerId = userId ? parseInt(userId, 10) : null;

  const [inbox, setInbox] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [peerName, setPeerName] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [err, setErr] = useState("");
  const [inboxErr, setInboxErr] = useState("");
  const [requests, setRequests] = useState<MatchReq[]>([]);
  const [reqErr, setReqErr] = useState("");
  const [busy, setBusy] = useState(false);

  const loadInbox = useCallback(() => {
    api
      .get<{ conversations: Conversation[] }>("/chat/inbox")
      .then((r) => {
        setInbox(r.data.conversations || []);
        setInboxErr("");
      })
      .catch((ex) => {
        const m = (ex as { response?: { data?: { error?: string } } })?.response?.data?.error;
        setInboxErr(m || "Could not load conversations.");
        setInbox([]);
      });
  }, []);

  const loadRequests = useCallback(() => {
    api
      .get<{ incoming: MatchReq[] }>("/match/requests")
      .then((r) => {
        setRequests(r.data.incoming || []);
        setReqErr("");
      })
      .catch(() => {
        setReqErr("Could not load requests.");
        setRequests([]);
      });
  }, []);

  const respondToRequest = async (matchId: number, status: "accepted" | "rejected") => {
    setBusy(true);
    try {
      await api.patch(`/match/${matchId}`, { status });
      loadRequests();
      loadInbox();
    } catch {
      setReqErr("Could not update request.");
    } finally {
      setBusy(false);
    }
  };

  const loadThread = useCallback(() => {
    if (!peerId || Number.isNaN(peerId)) return;
    api
      .get<{ messages: Msg[] }>(`/chat/with/${peerId}`)
      .then((r) => {
        setMessages(r.data.messages);
        setErr("");
      })
      .catch((ex) => {
        const m = (ex as { response?: { data?: { error?: string } } })?.response?.data?.error;
        setErr(m || "Cannot open chat.");
        setMessages([]);
      });
  }, [peerId]);

  useEffect(() => {
    if (!peerId || Number.isNaN(peerId)) {
      loadInbox();
      loadRequests();
      setMessages([]);
      setErr("");
      setPeerName(null);
    }
  }, [peerId, loadInbox, loadRequests]);

  useEffect(() => {
    if (peerId && !Number.isNaN(peerId)) {
      setErr("");
      loadThread();
      api
        .get<{ user: { name: string } }>(`/user/${peerId}`)
        .then((r) => setPeerName(r.data.user?.name || null))
        .catch(() => setPeerName(null));
    }
  }, [peerId, loadThread]);

  useEffect(() => {
    if (!me) return;
    const token = localStorage.getItem("access_token");
    if (!token) return;
    const s: Socket = io(apiBaseURL, {
      auth: { token },
      transports: ["websocket", "polling"],
    });
    s.on("new_message", (payload: { message: Msg }) => {
      const m = payload.message;
      const involvesMe = m.sender_id === me || m.receiver_id === me;
      if (!involvesMe) return;
      loadInbox();
      if (
        peerId &&
        !Number.isNaN(peerId) &&
        ((m.sender_id === peerId && m.receiver_id === me) ||
          (m.receiver_id === peerId && m.sender_id === me))
      ) {
        loadThread();
      }
    });
    return () => {
      s.disconnect();
    };
  }, [me, peerId, loadThread, loadInbox]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!peerId || !text.trim()) return;
    setErr("");
    try {
      await api.post("/chat/send", { receiver_id: peerId, message: text.trim() });
      setText("");
      loadThread();
      loadInbox();
    } catch (ex) {
      const m = (ex as { response?: { data?: { error?: string } } })?.response?.data?.error;
      setErr(m || "Send failed.");
    }
  }

  if (!peerId || Number.isNaN(peerId)) {
    return (
      <div className="max-w-lg mx-auto space-y-4">
        <h1 className="font-display text-2xl font-bold text-white">Messages</h1>
        <p className="text-slate-500 text-sm">
          Chats appear here after you and another tenant have an{" "}
          <strong className="text-slate-400">accepted</strong> roommate match. Open a thread below or
          use <strong className="text-slate-400">Open chat</strong> from their profile.
        </p>

        {(requests.length > 0 || reqErr) && (
          <div className="space-y-3 mb-6">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">
              Match Requests
            </h2>
            {reqErr && <p className="text-rose-300 text-sm">{reqErr}</p>}
            <ul className="space-y-2">
              {requests.map((req) => (
                <li key={req.id} className="glass rounded-xl p-4 flex items-center justify-between gap-4">
                  <div>
                    <Link to={`/roommates/${req.other_user?.id}`} className="text-white text-sm font-medium hover:underline">
                      {req.other_user?.name || `User #${req.other_user?.id}`}
                    </Link>
                    <p className="text-slate-500 text-xs mt-1">wants to be roommates</p>
                  </div>
                  <div className="flex gap-2 shrink-0">
                     <button
                      type="button"
                      disabled={busy}
                      className="btn-primary text-xs py-1 px-3"
                      onClick={() => respondToRequest(req.id, "accepted")}
                    >
                      Accept
                    </button>
                    <button
                      type="button"
                      disabled={busy}
                      className="btn-secondary text-xs py-1 px-3"
                      onClick={() => respondToRequest(req.id, "rejected")}
                    >
                      Decline
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mt-6 mb-2">
          Inbox
        </h2>

        {inboxErr && (
          <p className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-4 py-3 text-rose-300 text-sm">
            {inboxErr}
          </p>
        )}
        <ul className="space-y-2">
          {inbox.map((c) => (
            <li key={c.peer_id}>
              <Link
                to={`/messages/${c.peer_id}`}
                className="block glass rounded-xl p-4 hover:border-livora-500/30 border border-transparent transition"
              >
                <p className="text-white text-sm font-medium">{c.peer_name}</p>
                <p className="text-slate-500 text-xs truncate mt-1">
                  {c.last_message?.message ?? "No messages yet — say hello."}
                </p>
              </Link>
            </li>
          ))}
        </ul>
        {!inboxErr && inbox.length === 0 && (
          <p className="text-slate-600 text-sm py-6 text-center rounded-xl border border-slate-800/80 bg-slate-900/20">
            No conversations yet. Run a compatibility match, send a request, and after they accept you
            can chat here.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <Link to="/messages" className="text-sm text-livora-400 hover:underline">
        ← Inbox
      </Link>
      <h1 className="font-display text-2xl font-bold text-white">
        Chat · {peerName || `user #${peerId}`}
      </h1>
      {err && <p className="text-rose-300 text-sm">{err}</p>}
      <div className="glass rounded-2xl p-4 min-h-[320px] max-h-[480px] overflow-y-auto flex flex-col gap-3">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`rounded-lg px-3 py-2 max-w-[85%] text-sm ${
              m.sender_id === me
                ? "bg-livora-600/30 text-white self-end"
                : "bg-slate-800 text-slate-200 self-start"
            }`}
          >
            {m.message}
          </div>
        ))}
      </div>
      <form onSubmit={send} className="flex gap-2">
        <input
          className="input-field flex-1"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message…"
        />
        <button type="submit" className="btn-primary">
          Send
        </button>
      </form>
    </div>
  );
}
