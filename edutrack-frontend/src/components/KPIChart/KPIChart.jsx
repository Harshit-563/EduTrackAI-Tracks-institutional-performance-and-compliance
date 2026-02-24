import React from "react";

export default function KPIChart({ data = [] }) {
  const max = Math.max(1, ...data.map((d) => Number(d.value) || 0));

  return (
    <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4">
      <h3 className="text-sm font-semibold mb-3">KPI Trend</h3>
      <div className="space-y-2">
        {data.map((item) => {
          const value = Number(item.value) || 0;
          const width = `${Math.round((value / max) * 100)}%`;
          return (
            <div key={item.label}>
              <div className="flex justify-between text-xs mb-1">
                <span>{item.label}</span>
                <span>{value}</span>
              </div>
              <div className="h-2 bg-black/30 rounded">
                <div className="h-2 bg-emerald-500 rounded" style={{ width }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
