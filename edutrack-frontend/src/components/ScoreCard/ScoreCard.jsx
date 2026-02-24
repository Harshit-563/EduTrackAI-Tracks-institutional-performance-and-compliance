import React from "react";

export default function ScoreCard({ title, value }) {
  return (
    <div className="bg-gray-900/20 border border-gray-800 rounded-xl p-4">
      <div className="text-xs text-gray-400">{title}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  );
}
