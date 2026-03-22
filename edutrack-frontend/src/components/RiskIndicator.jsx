import React from "react";
import { AlertTriangle, CheckCircle, AlertCircle, Shield } from "lucide-react";

export default function RiskIndicator({ risk, title = "Risk Assessment" }) {
  if (!risk) return null;

  const riskLevel = risk.risk_level?.toLowerCase() || "unknown";
  const probability = risk.risk_probability.toFixed(1);
  const confidence = risk.confidence.toFixed(1);

  let bgColor = "bg-slate-800/40";
  let borderColor = "border-slate-700/40";
  let textColor = "text-slate-300";
  let badgeBg = "bg-slate-600";
  let badgeText = "text-slate-100";
  let icon = CheckCircle;
  let progressColor = "bg-slate-500";

  if (riskLevel === "high") {
    bgColor = "bg-red-500/10";
    borderColor = "border-red-500/40";
    textColor = "text-red-300";
    badgeBg = "bg-red-600";
    badgeText = "text-white";
    icon = AlertTriangle;
    progressColor = "bg-red-500";
  } else if (riskLevel === "medium") {
    bgColor = "bg-yellow-500/10";
    borderColor = "border-yellow-500/40";
    textColor = "text-yellow-300";
    badgeBg = "bg-yellow-600";
    badgeText = "text-white";
    icon = AlertCircle;
    progressColor = "bg-yellow-500";
  } else if (riskLevel === "low") {
    bgColor = "bg-green-500/10";
    borderColor = "border-green-500/40";
    textColor = "text-green-300";
    badgeBg = "bg-green-600";
    badgeText = "text-white";
    icon = Shield;
    progressColor = "bg-green-500";
  }

  const Icon = icon;

  return (
    <div className={`${bgColor} border ${borderColor} rounded-xl p-6 backdrop-blur-sm`}>
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="text-lg font-bold text-white">{title}</h3>
          <p className="text-xs text-slate-400 mt-1">Real-time ML Assessment</p>
        </div>
        <Icon className={`w-7 h-7 ${textColor}`} />
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className={`${badgeBg} ${badgeText} px-5 py-2.5 rounded-full font-bold uppercase text-sm tracking-wide`}>
          {riskLevel} Risk
        </div>
        <div>
          <div className="flex items-baseline gap-1">
            <p className="text-3xl font-bold text-white">{probability}</p>
            <p className="text-sm text-slate-400">%</p>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">Risk Probability</p>
        </div>
      </div>

      {/* Risk probability bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <p className="text-xs font-semibold text-slate-400">Risk Level</p>
          <p className="text-xs text-slate-500">{probability}%</p>
        </div>
        <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
          <div
            className={`h-full ${progressColor} rounded-full transition-all duration-500`}
            style={{ width: `${probability}%` }}
          ></div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-700/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 font-semibold uppercase">Confidence</p>
          <p className="text-2xl font-bold text-white mt-1">{confidence}%</p>
        </div>
        <div className="bg-slate-700/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 font-semibold uppercase">Status</p>
          <p className={`text-lg font-bold mt-1 ${textColor}`}>
            {riskLevel === "high" ? "🚨 Alert" : riskLevel === "medium" ? "⚠️ Caution" : "✅ Secure"}
          </p>
        </div>
      </div>
    </div>
  );
}
