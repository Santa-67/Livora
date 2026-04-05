import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="space-y-12">
      <section className="relative overflow-hidden rounded-3xl glass p-10 md:p-14">
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-livora-500/20 blur-3xl" />
        <div className="absolute -bottom-10 -left-10 h-48 w-48 rounded-full bg-teal-500/10 blur-3xl" />
        <div className="relative max-w-2xl">
          <p className="text-livora-400 text-sm font-semibold uppercase tracking-widest mb-3">
            Smart roommate matching · India
          </p>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-white leading-tight">
            Find flatmates who actually{" "}
            <span className="text-livora-400">fit your life</span>.
          </h1>
          <p className="mt-6 text-lg text-slate-400 leading-relaxed">
            Livora uses your trained RandomForest models for lifestyle clusters and
            a second model to flag suspicious profiles. Complete the lifestyle form,
            then open <strong className="text-slate-200">Match</strong> to see ML
            compatibility scores.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            {user ? (
              <>
                <Link to="/survey" className="btn-primary">
                  Set up ML profile
                </Link>
                <Link to="/roommates" className="btn-secondary">
                  View compatibility
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn-primary">
                  Get started
                </Link>
                <Link to="/login" className="btn-secondary">
                  I have an account
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <div className="grid md:grid-cols-3 gap-6">
        {[
          {
            title: "Lifestyle ML vector",
            desc: "Questionnaire maps to your notebook’s feature columns so roommate & fake models receive the right inputs.",
            to: "/survey",
            color: "from-livora-600/30 to-teal-600/20",
          },
          {
            title: "Compatibility score",
            desc: "Top matches show scores from cluster similarity (ML) or lifestyle heuristics if models are offline.",
            to: "/roommates",
            color: "from-violet-600/20 to-livora-600/20",
          },
          {
            title: "Trust scan",
            desc: "Run fake-profile detection on your saved vector before you meet someone.",
            to: "/trust",
            color: "from-amber-600/20 to-rose-600/20",
          },
        ].map((c) => (
          <Link
            key={c.title}
            to={c.to}
            className={`group rounded-2xl border border-slate-700/60 bg-gradient-to-br ${c.color} p-6 transition hover:border-livora-500/50`}
          >
            <h3 className="font-display text-lg font-semibold text-white group-hover:text-livora-300">
              {c.title}
            </h3>
            <p className="mt-2 text-sm text-slate-400 leading-relaxed">{c.desc}</p>
            <span className="mt-4 inline-block text-sm font-medium text-livora-400">
              Open →
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
