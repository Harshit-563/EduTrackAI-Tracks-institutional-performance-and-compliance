import React from "react";
import { Link } from "react-router-dom";

const features = [
  {
    title: "Document Intelligence",
    desc: "Upload compliance PDFs, run OCR + layout extraction, and generate structured fields with confidence signals.",
  },
  {
    title: "Compliance Agent",
    desc: "Compare extracted content against AICTE/UGC handbook requirements and return explainable compliance outcomes.",
  },
  {
    title: "Risk Engine",
    desc: "Combine DSS trends and institutional metrics to score risk and highlight anomalies for reviewers.",
  },
];

const steps = [
  { id: "01", title: "Institution Upload", desc: "Institute uploads mandatory documents and metadata." },
  { id: "02", title: "AI Validation", desc: "System extracts fields, computes DSS, and flags issues." },
  { id: "03", title: "Reviewer Decision", desc: "Reviewer verifies evidence and approves/rejects." },
  { id: "04", title: "Admin Oversight", desc: "Admins monitor throughput, model quality, and risk." },
];

export default function Landing() {
  return (
    <main className="min-h-screen text-gray-100 bg-[radial-gradient(circle_at_20%_20%,#1f2a44_0%,#0a0f1a_35%,#070b12_100%)]">
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-14">
        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-500/10 px-3 py-1 text-xs tracking-wide text-cyan-200">
          AI-Powered UGC/AICTE Compliance
        </div>

        <h1 className="mt-5 max-w-4xl text-4xl md:text-6xl leading-tight font-semibold">
          Institutional Approval Workflow,
          <span className="block text-cyan-300">Automated With Explainable AI</span>
        </h1>

        <p className="mt-5 max-w-3xl text-gray-300 text-base md:text-lg">
          Reduce manual review time using DSS scoring, rule-grounded compliance checks, and risk analytics designed for institutions, reviewers, and admins.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/login" className="px-5 py-3 rounded-lg bg-cyan-500 text-slate-900 font-semibold hover:bg-cyan-400">
            Sign In
          </Link>
          <Link to="/upload" className="px-5 py-3 rounded-lg border border-gray-600 hover:border-cyan-300 hover:text-cyan-200">
            Start Document Upload
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Metric label="Avg DSS Processing Time" value="< 90 sec" />
          <Metric label="Reviewer Effort Reduction" value="40-60%" />
          <Metric label="Compliance Explainability" value="Rule-Linked" />
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-10 border-t border-white/10">
        <h2 className="text-2xl md:text-3xl font-semibold">Core Capabilities</h2>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-5">
          {features.map((f) => (
            <article key={f.title} className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-cyan-200">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-300">{f.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-10 border-t border-white/10">
        <h2 className="text-2xl md:text-3xl font-semibold">Workflow</h2>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {steps.map((s) => (
            <article key={s.id} className="rounded-xl border border-white/10 p-5 bg-slate-900/40">
              <div className="text-cyan-300 text-xl font-bold">{s.id}</div>
              <h3 className="mt-2 font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-gray-300">{s.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-12 border-t border-white/10">
        <div className="rounded-2xl border border-cyan-400/30 bg-cyan-500/10 p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h3 className="text-2xl font-semibold">Ready to speed up approval reviews?</h3>
            <p className="mt-2 text-sm text-gray-300">Launch your compliance workflow with AI-assisted validation and human-in-the-loop review.</p>
          </div>
          <Link to="/login" className="px-5 py-3 rounded-lg bg-cyan-400 text-slate-900 font-semibold hover:bg-cyan-300 w-fit">
            Open Platform
          </Link>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-cyan-200">{value}</div>
    </div>
  );
}
