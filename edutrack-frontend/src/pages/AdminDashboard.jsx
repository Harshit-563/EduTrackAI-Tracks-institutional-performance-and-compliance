import React, { useMemo } from "react";

const KPI_DATA = [
  { label: "Institutions", value: 128, note: "Active this cycle" },
  { label: "Pending Reviews", value: 46, note: "Across all reviewers" },
  { label: "Avg DSS", value: 74, note: "Last 30 days" },
  { label: "High Risk", value: 9, note: "Needs escalation" },
];

const REVIEWER_STATS = [
  { name: "Ritika Sharma", assigned: 22, closed: 17, avg_turnaround: "9h", quality: "High" },
  { name: "Anil Verma", assigned: 18, closed: 14, avg_turnaround: "12h", quality: "Medium" },
  { name: "Sara Khan", assigned: 16, closed: 15, avg_turnaround: "7h", quality: "High" },
  { name: "Mohan Iyer", assigned: 13, closed: 10, avg_turnaround: "14h", quality: "Medium" },
];

const INSTITUTION_RISK = [
  { institution: "North Valley Institute", health_score: 82, risk: "Low", pending: 2 },
  { institution: "Delta Technical Campus", health_score: 54, risk: "High", pending: 6 },
  { institution: "Metro College of Engineering", health_score: 71, risk: "Medium", pending: 3 },
  { institution: "Westbridge Institute", health_score: 88, risk: "Low", pending: 1 },
  { institution: "Sunrise Polytechnic", health_score: 61, risk: "Medium", pending: 4 },
];

function RiskPill({ risk }) {
  const klass =
    risk === "Low"
      ? "bg-emerald-700/80"
      : risk === "Medium"
      ? "bg-amber-700/80"
      : "bg-rose-700/80";

  return <span className={`px-2 py-1 rounded text-xs text-white ${klass}`}>{risk}</span>;
}

export default function AdminDashboard() {
  const totals = useMemo(() => {
    const totalAssigned = REVIEWER_STATS.reduce((acc, r) => acc + r.assigned, 0);
    const totalClosed = REVIEWER_STATS.reduce((acc, r) => acc + r.closed, 0);
    const completion = totalAssigned ? Math.round((totalClosed / totalAssigned) * 100) : 0;
    return { totalAssigned, totalClosed, completion };
  }, []);

  return (
    <div className="min-h-screen bg-[#0f1720] text-gray-100 p-6 md:p-8">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-semibold">Admin Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">System-wide view of compliance throughput, reviewer productivity, and institutional risk.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3 mb-6">
        {KPI_DATA.map((item) => (
          <section key={item.label} className="rounded-xl border border-slate-800 bg-slate-900/35 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">{item.label}</div>
            <div className="text-2xl md:text-3xl font-semibold mt-2">{item.value}</div>
            <p className="text-xs text-slate-500 mt-1">{item.note}</p>
          </section>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5 mb-6">
        <section className="xl:col-span-2 rounded-xl border border-slate-800 bg-slate-900/35 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Reviewer Performance</h2>
            <span className="text-xs text-slate-400">Completion: {totals.completion}%</span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-800">
                  <th className="px-3 py-2">Reviewer</th>
                  <th className="px-3 py-2">Assigned</th>
                  <th className="px-3 py-2">Closed</th>
                  <th className="px-3 py-2">Avg Turnaround</th>
                  <th className="px-3 py-2">Quality</th>
                </tr>
              </thead>
              <tbody>
                {REVIEWER_STATS.map((row) => (
                  <tr key={row.name} className="border-b border-slate-800/70 hover:bg-slate-800/20">
                    <td className="px-3 py-3 font-medium">{row.name}</td>
                    <td className="px-3 py-3">{row.assigned}</td>
                    <td className="px-3 py-3">{row.closed}</td>
                    <td className="px-3 py-3">{row.avg_turnaround}</td>
                    <td className="px-3 py-3">{row.quality}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900/35 p-4">
          <h2 className="text-lg font-semibold mb-3">Ops Snapshot</h2>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between border-b border-slate-800/70 pb-2">
              <span className="text-slate-400">Review Backlog</span>
              <span className="font-medium">46</span>
            </li>
            <li className="flex justify-between border-b border-slate-800/70 pb-2">
              <span className="text-slate-400">Escalated Cases</span>
              <span className="font-medium">12</span>
            </li>
            <li className="flex justify-between border-b border-slate-800/70 pb-2">
              <span className="text-slate-400">Model Drift Alerts</span>
              <span className="font-medium">2</span>
            </li>
            <li className="flex justify-between">
              <span className="text-slate-400">SLA Breach Risk</span>
              <span className="font-medium">Medium</span>
            </li>
          </ul>
        </section>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/35 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Institution Risk Monitor</h2>
          <span className="text-xs text-slate-400">Health score derived from DSS + performance signals</span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-800">
                <th className="px-3 py-2">Institution</th>
                <th className="px-3 py-2">Health Score</th>
                <th className="px-3 py-2">Risk</th>
                <th className="px-3 py-2">Pending Docs</th>
              </tr>
            </thead>
            <tbody>
              {INSTITUTION_RISK.map((item) => (
                <tr key={item.institution} className="border-b border-slate-800/70 hover:bg-slate-800/20">
                  <td className="px-3 py-3 font-medium">{item.institution}</td>
                  <td className="px-3 py-3">{item.health_score}</td>
                  <td className="px-3 py-3"><RiskPill risk={item.risk} /></td>
                  <td className="px-3 py-3">{item.pending}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
