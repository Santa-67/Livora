import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth, effectiveRole, type UserRole } from "../context/AuthContext";

export default function RequireRole({
  allow,
  children,
}: {
  allow: UserRole[];
  children: ReactNode;
}) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center py-20 text-livora-400">Loading…</div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  const r = effectiveRole(user);
  if (!allow.includes(r)) {
    if (r === "owner") {
      return <Navigate to="/owner" replace />;
    }
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
