import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

export default function PerformanceChart({ predictions, type = "bar" }) {
  if (!predictions) return null;

  // Prepare data for bar chart
  if (type === "bar" && predictions.performance_prediction) {
    const performanceData = [
      {
        name: "Confidence",
        value: (predictions.performance_prediction.confidence * 100).toFixed(1),
      },
    ];

    return (
      <div className="bg-slate-700/50 border border-slate-600/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Performance Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#cbd5e1" />
            <YAxis stroke="#cbd5e1" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #475569",
                borderRadius: "8px",
              }}
              textStyle={{ color: "#e2e8f0" }}
            />
            <Legend />
            <Bar dataKey="value" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // Prepare data for pie chart
  if (type === "pie" && predictions.performance_prediction?.class_probabilities) {
    const pieData = Object.entries(
      predictions.performance_prediction.class_probabilities
    ).map(([name, value]) => ({
      name,
      value: (value * 100).toFixed(1),
    }));

    const COLORS = ["#667eea", "#764ba2", "#f59e0b", "#10b981"];

    return (
      <div className="bg-slate-700/50 border border-slate-600/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Performance Tier Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #475569",
                borderRadius: "8px",
              }}
              textStyle={{ color: "#e2e8f0" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return null;
}
