import React, { useEffect, useMemo, useState } from "react";
import client from "../api/api";

const FALLBACK_ROWS = [
  {
    rank: 1,
    institution: "North Valley Institute",
    avg_dss_score: 91,
    risk_score: 17,
    rank_score: 54,
    submission_count: 1,
  },
  {
    rank: 2,
    institution: "Delta Technical Campus",
    avg_dss_score: 58,
    risk_score: 50,
    rank_score: 54,
    submission_count: 1,
  },
  {
    rank: 3,
    institution: "Metro College of Engineering",
    avg_dss_score: 84,
    risk_score: 16,
    rank_score: 50,
    submission_count: 1,
  },
];

function scoreTone(score) {
  if (score >= 75) return "text-emerald-300";
  if (score >= 50) return "text-amber-300";
  return "text-rose-300";
}

function normalizeRow(item) {
  return {
    rank: Number(item.rank ?? item.Rank ?? 0),
    institution: String(item.institution ?? item["College Name"] ?? "").trim(),
    avg_dss_score: Number(item.avg_dss_score ?? item.Avg_Doc_DSS ?? 0),
    risk_score: Number(item.risk_score ?? item.Risk_Score ?? 0),
    rank_score: Number(item.rank_score ?? item.Rank_Score ?? 0),
    submission_count: item.submission_count ?? null,
  };
}

export default function RankList() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [source, setSource] = useState("-");

  useEffect(() => {
    let mounted = true;

    async function fetchRanks() {
      setLoading(true);
      setError("");

      try {
        const resp = await client.get("/institutions/rank-list");
        if (!mounted) return;

        const rawItems = Array.isArray(resp?.data?.items) ? resp.data.items : [];
        const items = rawItems.map(normalizeRow).filter((r) => r.institution);
        setRows(items.length ? items : FALLBACK_ROWS);
        setSource(resp?.data?.source || "api");
      } catch (e) {
        if (!mounted) return;
        setError(e?.message || "Failed to load rank list. Using fallback data.");
        setRows(FALLBACK_ROWS);
        setSource("fallback");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchRanks();
    return () => {
      mounted = false;
    };
  }, []);

  const summary = useMemo(() => {
    if (!rows.length) return { total: 0, topScore: 0, avgScore: 0 };
    const total = rows.length;
    const topScore = Number(rows[0]?.rank_score || 0);
    const avgScore = Math.round(rows.reduce((acc, r) => acc + Number(r.rank_score || 0), 0) / total);
    return { total, topScore, avgScore };
  }, [rows]);

  return (
    <div className="text-gray-100">
      <section className="panel p-5 md:p-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold">Institution Rank List</h1>
            <p className="mt-1 text-sm text-slate-300">
              Ranking formula: <code>(Avg_Doc_DSS + Risk_Score) / 2</code>
            </p>
          </div>
          <div className="text-xs text-slate-400">Source: {source}</div>
        </div>

        <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <SummaryCard label="Institutions" value={summary.total} />
          <SummaryCard label="Top Rank Score" value={summary.topScore} />
          <SummaryCard label="Average Rank Score" value={summary.avgScore} />
        </div>
      </section>

      {error && <div className="mt-4 panel-soft px-4 py-3 text-sm text-amber-200">{error}</div>}

      <section className="mt-4 panel-soft overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-300">Loading rank list...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700/70">
                  <th className="px-4 py-3">Rank</th>
                  <th className="px-4 py-3">Institution</th>
                  <th className="px-4 py-3">Avg DSS</th>
                  <th className="px-4 py-3">Risk Score</th>
                  <th className="px-4 py-3">Rank Score</th>
                  <th className="px-4 py-3">Submissions</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={`${r.institution}-${r.rank}`} className="border-b border-slate-800/60 hover:bg-slate-800/25">
                    <td className="px-4 py-3 font-semibold">#{r.rank}</td>
                    <td className="px-4 py-3">{r.institution}</td>
                    <td className="px-4 py-3">{r.avg_dss_score}</td>
                    <td className="px-4 py-3">{r.risk_score}</td>
                    <td className={`px-4 py-3 font-semibold ${scoreTone(Number(r.rank_score || 0))}`}>{r.rank_score}</td>
                    <td className="px-4 py-3">{r.submission_count ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function SummaryCard({ label, value }) {
  return (
    <div className="panel-soft p-4">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}
