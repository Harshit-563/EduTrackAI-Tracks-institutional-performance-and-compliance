import React, { useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AlertCircle, Download, RefreshCw, Target, TrendingUp } from "lucide-react";

const DASHBOARDS = [
  { id: "performance", label: "Performance", icon: "PA" },
  { id: "risk", label: "Risk Analysis", icon: "RI" },
  { id: "placement", label: "Placement", icon: "PL" },
  { id: "geographic", label: "Geographic", icon: "GE" },
];

const PERFORMANCE_DATA = [
  { score: 32, count: 15 },
  { score: 40, count: 45 },
  { score: 50, count: 120 },
  { score: 60, count: 380 },
  { score: 70, count: 890 },
  { score: 80, count: 1200 },
  { score: 90, count: 800 },
];

const RISK_DATA = [
  { risk: "High", count: 1069, percentage: 22.1 },
  { risk: "Low", count: 3762, percentage: 77.9 },
];

const PLACEMENT_DATA = [
  { year: "2022", rate: 55 },
  { year: "2023", rate: 62 },
  { year: "2024", rate: 68 },
];

const GEOGRAPHIC_DATA = [
  { state: "Maharashtra", institutions: 450, avgScore: 72 },
  { state: "Karnataka", institutions: 380, avgScore: 70 },
  { state: "Tamil Nadu", institutions: 320, avgScore: 74 },
  { state: "Telangana", institutions: 290, avgScore: 71 },
  { state: "Delhi", institutions: 210, avgScore: 76 },
];

function StatCard({ label, value, accent }) {
  return (
    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
      <p className="text-slate-400 text-sm mb-2">{label}</p>
      <p className={`text-3xl font-bold ${accent}`}>{value}</p>
    </div>
  );
}

export default function Analytics() {
  const [selectedDashboard, setSelectedDashboard] = useState("performance");
  const [loading, setLoading] = useState(false);

  const handleDownload = () => {
    setLoading(true);
    window.setTimeout(() => setLoading(false), 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950">
      <div className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/40 px-6 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-primary rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
            </div>
            <p className="text-slate-400 text-sm">System-wide performance and institutional metrics</p>
          </div>

          <button
            onClick={handleDownload}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 disabled:opacity-60 text-white rounded-lg font-medium transition"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Export
              </>
            )}
          </button>
        </div>
      </div>

      <div className="px-6 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {DASHBOARDS.map((dashboard) => (
              <button
                key={dashboard.id}
                onClick={() => setSelectedDashboard(dashboard.id)}
                className={`p-4 rounded-lg border transition ${
                  selectedDashboard === dashboard.id
                    ? "bg-gradient-primary/20 border-primary text-white"
                    : "bg-slate-800/40 border-slate-700/40 text-slate-400 hover:border-slate-600"
                }`}
              >
                <div className="text-sm font-bold mb-2">{dashboard.icon}</div>
                <div className="text-sm font-semibold">{dashboard.label}</div>
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {selectedDashboard === "performance" && (
              <>
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Score Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={PERFORMANCE_DATA}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="score" stroke="#cbd5e1" />
                      <YAxis stroke="#cbd5e1" />
                      <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
                      <Bar dataKey="count" fill="#5b6ee1" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Statistics</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                      <span className="text-slate-400">Average Score</span>
                      <span className="text-2xl font-bold text-primary">72.4</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                      <span className="text-slate-400">Total Institutions</span>
                      <span className="text-2xl font-bold text-blue-400">4,831</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                      <span className="text-slate-400">High Performers</span>
                      <span className="text-2xl font-bold text-green-400">2,000</span>
                    </div>
                  </div>
                </div>
              </>
            )}

            {selectedDashboard === "risk" && (
              <>
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Risk Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={RISK_DATA}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="risk" stroke="#cbd5e1" />
                      <YAxis stroke="#cbd5e1" />
                      <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
                      <Bar dataKey="count" fill="#ef4444" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6 flex flex-col justify-center">
                  <div className="space-y-4">
                    {RISK_DATA.map((item) => (
                      <div key={item.risk} className="p-4 bg-slate-700/30 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-slate-300">{item.risk} Risk</span>
                          <span className="font-bold text-white">{item.percentage}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${item.risk === "High" ? "bg-red-500" : "bg-green-500"}`}
                            style={{ width: `${item.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {selectedDashboard === "placement" && (
              <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6 lg:col-span-2">
                <h3 className="text-lg font-bold text-white mb-4">Placement Rate Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={PLACEMENT_DATA}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="year" stroke="#cbd5e1" />
                    <YAxis stroke="#cbd5e1" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
                    <Line type="monotone" dataKey="rate" stroke="#10b981" strokeWidth={3} dot={{ fill: "#10b981", r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {selectedDashboard === "geographic" && (
              <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6 lg:col-span-2">
                <h3 className="text-lg font-bold text-white mb-4">Top States by Institution Count</h3>
                <div className="space-y-3">
                  {GEOGRAPHIC_DATA.map((state) => (
                    <div key={state.state} className="p-4 bg-slate-700/20 rounded-lg border border-slate-700/40">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-slate-300 font-medium">{state.state}</span>
                        <div className="flex gap-4">
                          <span className="text-primary font-bold">{state.institutions} institutions</span>
                          <span className="text-green-400 font-bold">Avg: {state.avgScore}</span>
                        </div>
                      </div>
                      <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-primary" style={{ width: `${(state.institutions / 520) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm font-medium">Total Evaluated</p>
                  <p className="text-3xl font-bold text-white mt-2">4,831</p>
                </div>
                <Target className="w-8 h-8 text-primary" />
              </div>
            </div>
            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm font-medium">Avg Performance</p>
                  <p className="text-3xl font-bold text-green-400 mt-2">72.4%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-400" />
              </div>
            </div>
            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm font-medium">High Risk</p>
                  <p className="text-3xl font-bold text-red-400 mt-2">22.1%</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-400" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <StatCard label="Performance Score" value="72.4" accent="text-primary" />
            <StatCard label="Placement Growth" value="+13%" accent="text-green-400" />
            <StatCard label="States Covered" value="35" accent="text-blue-400" />
          </div>
        </div>
      </div>
    </div>
  );
}
