import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import ReviewerQueue from "./pages/ReviewerQueue";
import ReviewDocument from "./pages/ReviewDocument";
import InstituteDashboard from "./pages/InstituteDashboard";
import AdminDashboard from "./pages/AdminDashboard";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout><Landing /></Layout>} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/upload"
          element={<ProtectedRoute><Layout><Upload /></Layout></ProtectedRoute>}
        />

        <Route
          path="/reviewer"
          element={<ProtectedRoute><Layout><ReviewerQueue /></Layout></ProtectedRoute>}
        />

        <Route
          path="/reviewer/document/:id"
          element={<ProtectedRoute><Layout><ReviewDocument /></Layout></ProtectedRoute>}
        />

        <Route
          path="/institute"
          element={<ProtectedRoute><Layout><InstituteDashboard /></Layout></ProtectedRoute>}
        />

        <Route
          path="/admin"
          element={<ProtectedRoute><Layout><AdminDashboard /></Layout></ProtectedRoute>}
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

