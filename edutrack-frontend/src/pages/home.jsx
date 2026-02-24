// src/pages/Home.jsx
import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0f1720] text-gray-200">

      {/* ================= HERO SECTION ================= */}
      <section className="px-8 py-20 max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6 leading-tight">
            AI-Powered Institutional <br />
            <span className="text-indigo-400">Compliance & Review System</span>
          </h1>

          <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-8">
            Automate UGC & AICTE approval processes with intelligent document validation,
            compliance scoring, anomaly detection, and performance analytics.
          </p>

          <div className="flex justify-center gap-4">
            <Link
              to="/login"
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium"
            >
              Login
            </Link>

            <Link
              to="/institution/dashboard"
              className="px-6 py-3 border border-gray-700 hover:bg-gray-800 rounded-lg text-sm"
            >
              View Demo Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* ================= FEATURES SECTION ================= */}
      <section className="px-8 py-16 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-semibold text-center mb-12">
            Core AI Capabilities
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard
              title="Document Intelligence"
              desc="OCR + LayoutLM based document parsing to extract structured data from affidavits, financial statements and certificates."
            />

            <FeatureCard
              title="Compliance Scoring"
              desc="AI evaluates documents against UGC/AICTE handbook rules and generates DSS (Document Sufficiency Score)."
            />

            <FeatureCard
              title="Risk & Anomaly Detection"
              desc="Machine learning models detect abnormal trends in faculty growth, financial claims, and performance metrics."
            />
          </div>
        </div>
      </section>

      {/* ================= WORKFLOW SECTION ================= */}
      <section className="px-8 py-16 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-semibold text-center mb-12">
            How It Works
          </h2>

          <div className="grid md:grid-cols-4 gap-6 text-center">
            <WorkflowStep
              number="1"
              title="Upload"
              desc="Institution uploads required compliance documents."
            />

            <WorkflowStep
              number="2"
              title="AI Analysis"
              desc="System extracts fields and evaluates compliance."
            />

            <WorkflowStep
              number="3"
              title="Reviewer Decision"
              desc="Human reviewer verifies AI findings."
            />

            <WorkflowStep
              number="4"
              title="Approval / Correction"
              desc="Final approval or request for correction."
            />
          </div>
        </div>
      </section>

      {/* ================= ROLE SECTION ================= */}
      <section className="px-8 py-16 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-semibold text-center mb-12">
            Built For Every Role
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <RoleCard
              title="Institution"
              desc="Upload documents, track DSS, monitor compliance, and receive AI-driven insights."
            />

            <RoleCard
              title="Reviewer"
              desc="Review flagged documents, view AI extracted data, approve or reject efficiently."
            />

            <RoleCard
              title="Admin"
              desc="Monitor system health, manage institutions, configure compliance rules."
            />
          </div>
        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="border-t border-gray-800 py-6 text-center text-sm text-gray-500">
        © {new Date().getFullYear()} EduTrack AI — Smart Compliance Automation
      </footer>
    </div>
  );
}

/* ================= COMPONENTS ================= */

function FeatureCard({ title, desc }) {
  return (
    <div className="bg-gray-900/30 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <p className="text-sm text-gray-400">{desc}</p>
    </div>
  );
}

function WorkflowStep({ number, title, desc }) {
  return (
    <div className="bg-gray-900/20 border border-gray-800 p-6 rounded-xl">
      <div className="text-indigo-400 text-2xl font-bold mb-2">
        {number}
      </div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-400">{desc}</p>
    </div>
  );
}

function RoleCard({ title, desc }) {
  return (
    <div className="bg-gray-900/30 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <p className="text-sm text-gray-400">{desc}</p>
    </div>
  );
}