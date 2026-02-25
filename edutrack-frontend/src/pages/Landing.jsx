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
    <main className="text-gray-100">
      <section className="panel p-6 md:p-10">
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/35 bg-emerald-500/12 px-3 py-1 text-xs tracking-wide text-emerald-200">
          AI-Powered UGC/AICTE Compliance
        </div>

        <h1 className="mt-5 max-w-4xl text-4xl md:text-6xl leading-tight font-semibold">
          Institutional Approval Workflow,
          <span className="block text-amber-300">Automated With Explainable AI</span>
        </h1>

        <p className="mt-5 max-w-3xl text-gray-300 text-base md:text-lg">
          Reduce manual review time using DSS scoring, rule-grounded compliance checks, and risk analytics designed for institutions, reviewers, and admins.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/login" className="btn-primary px-5 py-3 rounded-lg font-semibold">
            Sign In
          </Link>
          <Link to="/upload" className="btn-subtle px-5 py-3 rounded-lg text-slate-100">
            Start Document Upload
          </Link>
        </div>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Metric label="Avg DSS Processing Time" value="< 90 sec" />
          <Metric label="Reviewer Effort Reduction" value="40-60%" />
          <Metric label="Compliance Explainability" value="Rule-Linked" />
        </div>
      </section>

      <section className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-5">
        {features.map((f) => (
          <article key={f.title} className="panel-soft p-5">
            <h3 className="text-lg font-semibold text-emerald-200">{f.title}</h3>
            <p className="mt-2 text-sm text-gray-300">{f.desc}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 panel-soft p-5 md:p-6">
        <h2 className="text-2xl md:text-3xl font-semibold">Workflow</h2>
        <div className="mt-5 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {steps.map((s) => (
            <article key={s.id} className="rounded-xl border border-white/10 p-5 bg-slate-900/40">
              <div className="text-amber-300 text-xl font-bold">{s.id}</div>
              <h3 className="mt-2 font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-gray-300">{s.desc}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="panel-soft p-4">
      <div className="text-xs uppercase tracking-wide text-gray-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-emerald-200">{value}</div>
    </div>
  );
}

