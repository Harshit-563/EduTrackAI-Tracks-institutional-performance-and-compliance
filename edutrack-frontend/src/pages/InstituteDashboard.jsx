import React from "react";
import { Building2, FileText, TrendingUp } from "lucide-react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const TREND_DATA = [
  { year: "2019", dss: 52 },
  { year: "2020", dss: 55 },
  { year: "2021", dss: 48 },
  { year: "2022", dss: 63 },
  { year: "2023", dss: 72 },
  { year: "2024", dss: 78 },
];

const SUBMISSIONS = [
  { id: 1, name: "Financial Audit 2024", dss: 82, status: "approved", date: "2024-09-01" },
  { id: 2, name: "Fire Safety Certificate", dss: 69, status: "review", date: "2024-10-15" },
  { id: 3, name: "Building Safety Report", dss: 58, status: "needs_update", date: "2024-08-05" },
];

const QUICK_STATS = [
  { label: "Total Submissions", value: "12", accent: "text-white" },
  { label: "Approved", value: "9", accent: "text-green-400" },
  { label: "Under Review", value: "2", accent: "text-yellow-400" },
  { label: "Needs Update", value: "1", accent: "text-red-400" },
];

function getStatusColor(status) {
  if (status === "approved") return "bg-green-500/20 text-green-300 border-green-500/30";
  if (status === "review") return "bg-blue-500/20 text-blue-300 border-blue-500/30";
  if (status === "needs_update") return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
  return "bg-red-500/20 text-red-300 border-red-500/30";
}

function getStatusLabel(status) {
  if (status === "needs_update") return "Needs Update";
  if (status === "review") return "In Review";
  if (status === "approved") return "Approved";
  return "Rejected";
}

export default function InstituteDashboard() {
  const overview = {
    name: "Demo Institute of Technology",
    dss: 78,
    compliance: 74,
    pending: 2,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Institution Dashboard</h1>
          </div>
          <p className="text-slate-400">{overview.name}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Avg DSS Score</p>
            <p className="text-3xl font-bold text-green-400">{overview.dss}</p>
            <p className="text-xs text-slate-500 mt-2">Document Sufficiency</p>
          </div>
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Compliance Rate</p>
            <p className="text-3xl font-bold text-blue-400">{overview.compliance}%</p>
            <p className="text-xs text-slate-500 mt-2">Current Status</p>
          </div>
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Pending Reviews</p>
            <p className="text-3xl font-bold text-yellow-400">{overview.pending}</p>
            <p className="text-xs text-slate-500 mt-2">Awaiting Action</p>
          </div>
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Status</p>
            <p className="text-2xl font-bold text-primary">Active</p>
            <p className="text-xs text-slate-500 mt-2">Compliant</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2 bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              DSS Trend
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={TREND_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="year" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
                <Line type="monotone" dataKey="dss" stroke="#5b6ee1" strokeWidth={3} dot={{ fill: "#5b6ee1", r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gradient-primary/10 border border-primary/30 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Quick Stats</h3>
            <div className="space-y-4">
              {QUICK_STATS.map((stat) => (
                <div key={stat.label} className="p-3 bg-slate-700/30 rounded-lg">
                  <p className="text-xs text-slate-400">{stat.label}</p>
                  <p className={`text-2xl font-bold mt-1 ${stat.accent}`}>{stat.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Recent Submissions
          </h3>
          <div className="space-y-3">
            {SUBMISSIONS.map((submission) => (
              <div
                key={submission.id}
                className="flex items-center justify-between p-4 bg-slate-700/20 rounded-lg border border-slate-700/40 hover:border-slate-600/60 transition"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-2 h-2 bg-primary rounded-full" />
                  <div>
                    <p className="text-slate-300 font-medium">{submission.name}</p>
                    <p className="text-xs text-slate-500">{submission.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xl font-bold text-primary">{submission.dss}</span>
                  <span className={`px-3 py-1 rounded-full border text-xs font-medium ${getStatusColor(submission.status)}`}>
                    {getStatusLabel(submission.status)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
