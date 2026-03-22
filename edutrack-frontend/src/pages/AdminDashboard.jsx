import React, { useState } from "react";
import { Users, Building2, FileCheck, AlertTriangle, TrendingUp, BarChart3 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const INSTITUTIONS_DATA = [
  { name: "Demo Tech", dss: 78, compliance: 74, status: "active" },
  { name: "State University", dss: 85, compliance: 82, status: "active" },
  { name: "Tech Institute", dss: 62, compliance: 58, status: "warning" },
  { name: "College of Arts", dss: 71, compliance: 68, status: "active" },
  { name: "Engineering College", dss: 88, compliance: 86, status: "active" },
];

const SUBMISSION_STATUS = [
  { name: "Approved", value: 45, color: "#10b981" },
  { name: "Review", value: 18, color: "#3b82f6" },
  { name: "Needs Update", value: 12, color: "#f59e0b" },
  { name: "Rejected", value: 5, color: "#ef4444" },
];

const PERFORMANCE_DATA = [
  { month: "Jan", submissions: 15, approvals: 12 },
  { month: "Feb", submissions: 22, approvals: 18 },
  { month: "Mar", submissions: 28, approvals: 25 },
  { month: "Apr", submissions: 24, approvals: 21 },
  { month: "May", submissions: 32, approvals: 29 },
  { month: "Jun", submissions: 38, approvals: 35 },
];

const COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"];

export default function AdminDashboard() {
  const [stats] = useState({
    totalInstitutions: 12,
    activeSubmissions: 80,
    avgDss: 76,
    systemHealth: 98,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          </div>
          <p className="text-slate-400">System-wide compliance and performance monitoring</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-400 text-sm">Total Institutions</p>
              <Building2 className="w-5 h-5 text-blue-400" />
            </div>
            <p className="text-3xl font-bold text-blue-400">{stats.totalInstitutions}</p>
            <p className="text-xs text-slate-500 mt-2">Active members</p>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-400 text-sm">Active Submissions</p>
              <FileCheck className="w-5 h-5 text-green-400" />
            </div>
            <p className="text-3xl font-bold text-green-400">{stats.activeSubmissions}</p>
            <p className="text-xs text-slate-500 mt-2">Under processing</p>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-400 text-sm">Avg DSS Score</p>
              <TrendingUp className="w-5 h-5 text-purple-400" />
            </div>
            <p className="text-3xl font-bold text-purple-400">{stats.avgDss}</p>
            <p className="text-xs text-slate-500 mt-2">Document sufficiency</p>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-400 text-sm">System Health</p>
              <AlertTriangle className="w-5 h-5 text-green-400" />
            </div>
            <p className="text-3xl font-bold text-green-400">{stats.systemHealth}%</p>
            <p className="text-xs text-slate-500 mt-2">Operational</p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Performance Chart */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Submissions & Approvals Trend
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={PERFORMANCE_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #475569" }} />
                <Legend />
                <Bar dataKey="submissions" fill="#5b6ee1" radius={[8, 8, 0, 0]} />
                <Bar dataKey="approvals" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Submission Status */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Submission Status Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={SUBMISSION_STATUS} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                  {SUBMISSION_STATUS.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Institutions Table */}
        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary" />
            Institution Performance
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/40">
                  <th className="text-left px-4 py-3 text-slate-400 text-sm font-semibold">Institution</th>
                  <th className="text-left px-4 py-3 text-slate-400 text-sm font-semibold">DSS Score</th>
                  <th className="text-left px-4 py-3 text-slate-400 text-sm font-semibold">Compliance</th>
                  <th className="text-left px-4 py-3 text-slate-400 text-sm font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {INSTITUTIONS_DATA.map((inst, idx) => (
                  <tr key={idx} className="border-b border-slate-700/20 hover:bg-slate-700/10 transition">
                    <td className="px-4 py-3 text-slate-300">{inst.name}</td>
                    <td className="px-4 py-3">
                      <span className="text-lg font-bold text-primary">{inst.dss}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-slate-700 rounded-full h-2 max-w-xs">
                          <div className="bg-primary h-2 rounded-full" style={{ width: `${inst.compliance}%` }}></div>
                        </div>
                        <span className="text-sm text-slate-400">{inst.compliance}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${inst.status === "active" ? "bg-green-500/20 text-green-300" : "bg-yellow-500/20 text-yellow-300"}`}>
                        {inst.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
