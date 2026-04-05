import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import RequireRole from "./components/RequireRole";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Listings from "./pages/Listings";
import RoommateMatch from "./pages/RoommateMatch";
import RoommateDetail from "./pages/RoommateDetail";
import LifestyleSurvey from "./pages/LifestyleSurvey";
import TrustCheck from "./pages/TrustCheck";
import Profile from "./pages/Profile";
import OwnerListings from "./pages/OwnerListings";
import AdminDashboard from "./pages/AdminDashboard";
import MessagesPage from "./pages/MessagesPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/listings" element={<Listings />} />
            <Route
              path="/roommates/:userId"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <RoommateDetail />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/roommates"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <RoommateMatch />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/survey"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <LifestyleSurvey />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/trust"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <TrustCheck />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/messages/:userId"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <MessagesPage />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/messages"
              element={
                <RequireAuth>
                  <RequireRole allow={["tenant", "admin"]}>
                    <MessagesPage />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/owner"
              element={
                <RequireAuth>
                  <RequireRole allow={["owner", "admin"]}>
                    <OwnerListings />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/admin"
              element={
                <RequireAuth>
                  <RequireRole allow={["admin"]}>
                    <AdminDashboard />
                  </RequireRole>
                </RequireAuth>
              }
            />
            <Route
              path="/profile"
              element={
                <RequireAuth>
                  <Profile />
                </RequireAuth>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
