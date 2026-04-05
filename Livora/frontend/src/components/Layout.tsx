import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth, effectiveRole } from "../context/AuthContext";

type NavItem = { to: string; label: string };

export default function Layout() {
  const { user, logout } = useAuth();
  const role = user ? effectiveRole(user) : "tenant";

  const items: NavItem[] = [{ to: "/", label: "Home" }];

  if (role === "owner") {
    items.push({ to: "/listings", label: "Browse" }, { to: "/owner", label: "My listings" });
  } else if (role === "admin") {
    items.push(
      { to: "/listings", label: "Listings" },
      { to: "/admin", label: "Admin" },
      { to: "/roommates", label: "Match" },
      { to: "/survey", label: "Lifestyle ML" },
      { to: "/trust", label: "Trust scan" },
      { to: "/messages", label: "Messages" }
    );
  } else {
    items.push(
      { to: "/listings", label: "Listings" },
      { to: "/roommates", label: "Match" },
      { to: "/survey", label: "Lifestyle ML" },
      { to: "/trust", label: "Trust scan" },
      { to: "/messages", label: "Messages" }
    );
  }

  if (user) {
    items.push({ to: "/profile", label: "Profile" });
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 border-b border-slate-800/80 glass">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <Link to="/" className="font-display text-xl font-bold tracking-tight">
            <span className="text-livora-400">Livora</span>
            <span className="text-slate-400 font-normal text-sm ml-2">India · roommate finder</span>
          </Link>
          <nav className="hidden lg:flex flex-wrap items-center gap-1 max-w-[60%] justify-end">
            {items.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `rounded-lg px-2.5 py-2 text-sm font-medium transition ${
                    isActive
                      ? "bg-livora-600/20 text-livora-300"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-3 shrink-0">
            {user ? (
              <>
                <span className="text-xs text-slate-500 capitalize hidden sm:inline">
                  {role}
                </span>
                <span className="text-sm text-slate-400 max-w-[120px] truncate hidden sm:inline">
                  {user.name}
                </span>
                <button type="button" className="btn-secondary text-xs py-2" onClick={logout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-secondary text-sm py-2">
                  Log in
                </Link>
                <Link to="/register" className="btn-primary text-sm py-2">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        Livora · India · ML-powered roommate compatibility
      </footer>
    </div>
  );
}
