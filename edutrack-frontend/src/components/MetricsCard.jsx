import React from "react";

export default function MetricsCard({ label, value, type = "number", icon: Icon }) {
  let valueColor = "text-slate-200";
  let bgColor = "bg-slate-800/40";
  let borderColor = "border-slate-700/40";
  let iconColor = "text-slate-500";

  if (type === "percentage") {
    const numValue = parseFloat(value);
    if (numValue >= 80) {
      valueColor = "text-green-400";
      bgColor = "bg-green-500/10";
      borderColor = "border-green-500/30";
      iconColor = "text-green-400";
    } else if (numValue >= 60) {
      valueColor = "text-yellow-400";
      bgColor = "bg-yellow-500/10";
      borderColor = "border-yellow-500/30";
      iconColor = "text-yellow-400";
    } else {
      valueColor = "text-red-400";
      bgColor = "bg-red-500/10";
      borderColor = "border-red-500/30";
      iconColor = "text-red-400";
    }
  } else if (type === "text" && value.includes("Excellent")) {
    valueColor = "text-primary_light";
    bgColor = "bg-primary/10";
    borderColor = "border-primary/40";
  }

  return (
    <div className={`${bgColor} border ${borderColor} rounded-xl p-5 backdrop-blur-sm hover:bg-slate-800/60 transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            {label}
          </p>
          <p className={`text-3xl font-bold ${valueColor}`}>{value}</p>
        </div>
        {Icon && (
          <div className="ml-4 p-3 bg-slate-700/30 rounded-lg">
            <Icon className={`w-6 h-6 ${iconColor}`} />
          </div>
        )}
      </div>
    </div>
  );
}
