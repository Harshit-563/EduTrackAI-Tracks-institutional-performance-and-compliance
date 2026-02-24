import React, { useEffect, useState } from "react";
import client from "../api/api";

const FALLBACK_OVERVIEW = {
  institution_name: "Demo Institute of Technology",
  avg_dss: 78,
  compliance: 64,
  pending_reviews: 3,
};

const FALLBACK_TREND = [
  { year: "2019", dss: 52 },
  { year: "2020", dss: 55 },
  { year: "2021", dss: 48 },
  { year: "2022", dss: 63 },
  { year: "2023", dss: 72 },
];

const FALLBACK_SUBMISSIONS = [
  { id: "S001", doc_type: "financial_audit", name: "audited_financials_2023.pdf", dss: 82, status: "approved", uploaded_at: "2024-09-01" },
  { id: "S002", doc_type: "fire_safety_certificate", name: "fire_safety_2024.pdf", dss: 69, status: "under_review", uploaded_at: "2024-10-15" },
  { id: "S003", doc_type: "building_safety", name: "building_safety_report.pdf", dss: 58, status: "needs_correction", uploaded_at: "2024-08-05" },
];

function StatusPill({ status }) {
  const map = {
    approved: "bg-green-700",
    under_review: "bg-blue-700",
    needs_correction: "bg-yellow-600",
    rejected: "bg-red-700",
  };
  return <span className={`px-2 py-1 rounded text-xs text-white ${map[status] || "bg-gray-700"}`}>{status}</span>;
}

export default function InstituteDashboard() {
  const [overview, setOverview] = useState(FALLBACK_OVERVIEW);
  const [trend, setTrend] = useState(FALLBACK_TREND);
  const [submissions, setSubmissions] = useState(FALLBACK_SUBMISSIONS);

  useEffect(() => {
    let mounted = true;

    async function fetchAll() {
      try {
        const [ov, tr, subs] = await Promise.allSettled([
          client.get("/institutions/inst_demo/overview"),
          client.get("/institutions/inst_demo/dss-trend"),
          client.get("/institutions/inst_demo/submissions"),
        ]);

        if (!mounted) return;

        if (ov.status === "fulfilled" && ov.value.data) setOverview(ov.value.data);
        if (tr.status === "fulfilled" && Array.isArray(tr.value.data)) setTrend(tr.value.data);
        if (subs.status === "fulfilled" && Array.isArray(subs.value.data)) setSubmissions(subs.value.data);
      } catch {
        // fallback only
      }
    }

    fetchAll();
    return () => {
      mounted = false;
    };
  }, []);

  const trendMax = Math.max(1, ...trend.map((t) => Number(t.dss) || 0));

  return (
    <div className="min-h-screen bg-[#0f1720] text-gray-200 p-8">
      <h1 className="text-3xl font-bold">{overview.institution_name}</h1>
      <p className="text-sm text-gray-400 mb-6">Overview of submissions and DSS trends.</p>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4"><div className="text-sm text-gray-400">Average DSS</div><div className="text-3xl font-bold">{overview.avg_dss}</div></div>
        <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4"><div className="text-sm text-gray-400">Compliance</div><div className="text-3xl font-bold">{overview.compliance}%</div></div>
        <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4"><div className="text-sm text-gray-400">Pending reviews</div><div className="text-3xl font-bold">{overview.pending_reviews}</div></div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-900/20 border border-gray-800 rounded-xl p-4">
          <h2 className="text-lg font-semibold mb-3">DSS Trend</h2>
          <div className="space-y-2">
            {trend.map((row) => (
              <div key={row.year}>
                <div className="flex justify-between text-xs mb-1"><span>{row.year}</span><span>{row.dss}</span></div>
                <div className="h-2 bg-black/30 rounded"><div className="h-2 bg-emerald-500 rounded" style={{ width: `${Math.round(((Number(row.dss) || 0) / trendMax) * 100)}%` }} /></div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4">
          <h2 className="text-lg font-semibold mb-3">Recent submissions</h2>
          <ul className="space-y-2 text-sm">
            {submissions.map((s) => (
              <li key={s.id} className="p-2 rounded border border-gray-800 bg-black/10">
                <div className="font-medium">{s.name}</div>
                <div className="text-xs text-gray-400">{s.doc_type} | DSS {s.dss}</div>
                <div className="mt-1"><StatusPill status={s.status} /></div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
