import React, { useMemo, useState } from "react";
import { AlertCircle, Trophy } from "lucide-react";

import rankListCsv from "../../../data/raw/college_rank_list.csv?raw";

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",").map((header) => header.trim());

  return lines.slice(1).map((line) => {
    const values = line.split(",").map((value) => value.trim());
    return headers.reduce((row, header, index) => {
      row[header] = values[index] ?? "";
      return row;
    }, {});
  });
}

function getScoreColor(score) {
  if (score >= 90) return "text-green-400 bg-green-500/10";
  if (score >= 80) return "text-blue-400 bg-blue-500/10";
  if (score >= 70) return "text-yellow-400 bg-yellow-500/10";
  return "text-red-400 bg-red-500/10";
}

function getRiskColor(score) {
  if (score >= 85) return "text-green-400";
  if (score >= 70) return "text-yellow-400";
  return "text-red-400";
}

export default function RankList() {
  const [sortBy, setSortBy] = useState("rank_score");

  const ranks = useMemo(
    () =>
      parseCsv(rankListCsv).map((item) => ({
        rank: Number(item.Rank) || 0,
        name: item["College Name"] || "Unknown Institution",
        avgDocDss: Number(item.Avg_Doc_DSS) || 0,
        riskScore: Number(item.Risk_Score) || 0,
        rankScore: Number(item.Rank_Score) || 0,
      })),
    []
  );

  const sortedRanks = useMemo(() => {
    const next = [...ranks];

    if (sortBy === "rank") {
      return next.sort((a, b) => a.rank - b.rank);
    }

    if (sortBy === "risk") {
      return next.sort((a, b) => b.riskScore - a.riskScore);
    }

    if (sortBy === "dss") {
      return next.sort((a, b) => b.avgDocDss - a.avgDocDss);
    }

    return next.sort((a, b) => b.rankScore - a.rankScore);
  }, [ranks, sortBy]);

  const highestRankScore = ranks.reduce((max, item) => Math.max(max, item.rankScore), 0);
  const averageDocDss = ranks.length
    ? (ranks.reduce((total, item) => total + item.avgDocDss, 0) / ranks.length).toFixed(2)
    : "0.00";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <Trophy className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Institution Rankings</h1>
          </div>
          <p className="text-slate-400">Live ranking data loaded from the official college rank CSV.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Total Institutions</p>
            <p className="text-3xl font-bold text-white">{ranks.length}</p>
          </div>
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Highest Rank Score</p>
            <p className="text-3xl font-bold text-green-400">{highestRankScore.toFixed(2)}</p>
          </div>
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-2">Average Doc DSS</p>
            <p className="text-3xl font-bold text-blue-400">{averageDocDss}</p>
          </div>
        </div>

        <div className="mb-6 flex gap-3 flex-wrap">
          {[
            { id: "rank_score", label: "Rank Score" },
            { id: "risk", label: "Risk Score" },
            { id: "dss", label: "Avg Doc DSS" },
            { id: "rank", label: "Official Rank" },
          ].map((option) => (
            <button
              key={option.id}
              onClick={() => setSortBy(option.id)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                sortBy === option.id
                  ? "bg-gradient-primary text-white"
                  : "bg-slate-800/40 border border-slate-700/40 text-slate-300 hover:border-slate-600"
              }`}
            >
              Sort by {option.label}
            </button>
          ))}
        </div>

        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/40 bg-slate-900/50">
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Rank</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase">Institution</th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-slate-400 uppercase">Avg Doc DSS</th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-slate-400 uppercase">Risk Score</th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-slate-400 uppercase">Rank Score</th>
                </tr>
              </thead>
              <tbody>
                {sortedRanks.map((inst, idx) => (
                  <tr key={`${inst.rank}-${inst.name}`} className="border-b border-slate-700/20 hover:bg-slate-700/20 transition">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {idx === 0 && <Trophy className="w-5 h-5 text-yellow-400" />}
                        {idx === 1 && <Trophy className="w-5 h-5 text-slate-400" />}
                        {idx === 2 && <Trophy className="w-5 h-5 text-orange-400" />}
                        <span className="text-white font-semibold">{inst.rank}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-white font-medium">{inst.name}</p>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-3 py-1 rounded-lg font-bold ${getScoreColor(inst.avgDocDss)}`}>
                        {inst.avgDocDss.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`font-semibold ${getRiskColor(inst.riskScore)}`}>{inst.riskScore.toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4 text-center text-primary font-semibold">{inst.rankScore.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-8 p-6 bg-gradient-primary/10 border border-primary/30 rounded-xl flex items-start gap-4">
          <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-white font-semibold mb-2">Ranking Source</h3>
            <p className="text-slate-300 text-sm">
              This view now uses the real dataset from <span className="font-mono">data/raw/college_rank_list.csv</span>. Rankings reflect the source file&apos;s official rank, average document DSS, risk score, and combined rank score.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
