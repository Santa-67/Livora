import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, clearTokens, setTokens } from "../api/client";

export type UserRole = "tenant" | "owner" | "admin";

export type User = {
  id: number;
  email: string;
  name: string;
  role?: UserRole;
  budget?: number;
  lifestyle?: Record<string, unknown>;
  gender?: string;
  bio?: string;
  avatar_url?: string;
  is_admin?: boolean;
};

/** Match backend get_user_role: is_admin implies admin for routing. */
export function effectiveRole(user: User | null): UserRole {
  if (!user) return "tenant";
  if (user.is_admin || user.role === "admin") return "admin";
  const r = (user.role || "tenant").toLowerCase();
  if (r === "owner") return "owner";
  return "tenant";
}

type AuthCtx = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (
    email: string,
    password: string,
    name: string,
    accountType: "tenant" | "owner"
  ) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get<{ user: User }>("/user/profile");
      setUser(data.user);
    } catch {
      setUser(null);
      clearTokens();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    const { data } = await api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>("/auth/login", { email, password });
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
    return data.user;
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    accountType: "tenant" | "owner"
  ) => {
    const { data } = await api.post<{
      access_token: string;
      refresh_token: string;
      user: User;
    }>("/auth/register", { email, password, name, account_type: accountType });
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <Ctx.Provider
      value={{ user, loading, login, register, logout, refreshUser }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}
