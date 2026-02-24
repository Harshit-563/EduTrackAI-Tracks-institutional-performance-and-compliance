import React, { useEffect, useMemo, useState } from "react";
import client from "../api/api";

const FALLBACK_SUBMISSIONS = [
  {
    id: "SUB-101",
    institution: "North Valley Institute",
    doc_type: "fire_safety_certificate",
    dss: 91,
    status: "needs_manual_review",
    uploaded_at: "2026-01-19",
    flags: ["Expiry date found", "Signature confidence medium"],
    extracted_fields: {
      certificate_no: "FS-2026-0092",
      valid_till: "2027-12-31",
      authority: "City Fire Department",
    },
  },
  {
    id: "SUB-102",
    institution: "Delta Technical Campus",
    doc_type: "financial_audit",
    dss: 58,
    status: "low_confidence",
    uploaded_at: "2026-01-17",
    flags: ["Stamp missing", "Auditor signature unclear"],
    extracted_fields: {
      fiscal_year: "2024-25",
      auditor: "M/S K Sharma & Co.",
      net_surplus: "1.8 Cr",
    },
  },
  {
    id: "SUB-103",
    institution: "Metro College of Engineering",
    doc_type: "faculty_list",
    dss: 84,
    status: "parsed",
    uploaded_at: "2026-01-14",
    flags: ["2 rows with missing designation"],
    extracted_fields: {
      faculty_count: 126,
      phd_count: 48,
    },
  },
  {
    id: "SUB-104",
    institution: "Westbridge Institute",
    doc_type: "affiliation_letter",
    dss: 96,
    status: "approved",
    uploaded_at: "2026-01-11",
    flags: [],
    extracted_fields: {
      affiliation_id: "UGC-AFF-2026-781",
      valid_till: "2028-03-31",
    },
  },
];

const STATUS_LABEL = {
  parsed: "Parsed",
  needs_manual_review: "Needs Review",
  low_confidence: "Low Confidence",
  approved: "Approved",
  rejected: "Rejected",
  request_correction: "Correction Requested",
};

const STATUS_CLASS = {
  parsed: "bg-blue-700/70",
  needs_manual_review: "bg-amber-600/80",
  low_confidence: "bg-red-700/80",
  approved: "bg-emerald-700/80",
  rejected: "bg-rose-800/80",
  request_correction: "bg-yellow-700/80",
};

function StatusPill({ status }) {
  return (
    <span className={`px-2 py-1 rounded text-xs text-white ${STATUS_CLASS[status] || "bg-gray-700"}`}>
      {STATUS_LABEL[status] || status}
    </span>
  );
}

function safeDate(dateValue) {
  const d = new Date(dateValue);
  if (Number.isNaN(d.getTime())) return dateValue;
  return d.toLocaleDateString();
}

export default function ReviewerQueue() {
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [note, setNote] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    let mounted = true;

    async function loadQueue() {
      setLoading(true);
      try {
        const resp = await client.get("/reviewer/queue");
        if (!mounted) return;
        const payload = Array.isArray(resp.data) ? resp.data : FALLBACK_SUBMISSIONS;
        setRows(payload.length ? payload : FALLBACK_SUBMISSIONS);
      } catch {
        if (mounted) setRows(FALLBACK_SUBMISSIONS);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadQueue();
    return () => {
      mounted = false;
    };
  }, []);

  const filteredRows = useMemo(() => {
    const q = search.trim().toLowerCase();

    return rows
      .filter((item) => (statusFilter === "all" ? true : item.status === statusFilter))
      .filter((item) => {
        if (!q) return true;
        return (
          String(item.id || "").toLowerCase().includes(q) ||
          String(item.institution || "").toLowerCase().includes(q) ||
          String(item.doc_type || "").toLowerCase().includes(q)
        );
      })
      .sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
  }, [rows, search, statusFilter]);

  const metrics = useMemo(() => {
    const total = rows.length;
    const pending = rows.filter((r) => r.status === "needs_manual_review").length;
    const low = rows.filter((r) => r.status === "low_confidence").length;
    const avg = total ? Math.round(rows.reduce((acc, cur) => acc + Number(cur.dss || 0), 0) / total) : 0;

    return { total, pending, low, avg };
  }, [rows]);

  async function applyAction(submissionId, action) {
    setActionLoading(true);
    const previous = rows;
    setRows((cur) => cur.map((item) => (item.id === submissionId ? { ...item, status: action } : item)));

    try {
      await client.post(`/reviews/${submissionId}/action`, {
        action,
        notes: note,
      });
      setNote("");
    } catch {
      setRows(previous);
    } finally {
      setActionLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0f1720] text-gray-100 p-6 md:p-8">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-semibold">Reviewer Queue</h1>
          <p className="text-sm text-gray-400 mt-1">Review AI-flagged submissions and finalize decisions.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard label="Total Submissions" value={metrics.total} />
        <StatCard label="Pending Review" value={metrics.pending} tone="amber" />
        <StatCard label="Low Confidence" value={metrics.low} tone="red" />
        <StatCard label="Avg DSS" value={metrics.avg} tone="cyan" />
      </div>

      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 mb-4 flex flex-col md:flex-row gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by institution, document type, or submission ID"
          className="w-full md:w-[28rem] rounded-lg bg-black/20 border border-slate-700 px-3 py-2 text-sm"
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg bg-black/20 border border-slate-700 px-3 py-2 text-sm"
        >
          <option value="all">All Status</option>
          <option value="needs_manual_review">Needs Review</option>
          <option value="low_confidence">Low Confidence</option>
          <option value="parsed">Parsed</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/30 overflow-x-auto">
        {loading ? (
          <div className="p-10 text-center text-sm text-gray-400">Loading reviewer queue...</div>
        ) : (
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-800">
                <th className="px-4 py-3">Submission</th>
                <th className="px-4 py-3">Institution</th>
                <th className="px-4 py-3">DSS</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Uploaded</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row) => (
                <tr key={row.id} className="border-b border-slate-800/80 hover:bg-slate-800/20">
                  <td className="px-4 py-3">
                    <div className="font-medium">{row.doc_type}</div>
                    <div className="text-xs text-slate-400">{row.id}</div>
                  </td>
                  <td className="px-4 py-3">{row.institution}</td>
                  <td className="px-4 py-3 font-semibold">{row.dss}</td>
                  <td className="px-4 py-3"><StatusPill status={row.status} /></td>
                  <td className="px-4 py-3 text-slate-300">{safeDate(row.uploaded_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => setSelected(row)} className="px-2 py-1 rounded bg-slate-700 text-xs">View</button>
                      <button onClick={() => applyAction(row.id, "approved")} disabled={actionLoading} className="px-2 py-1 rounded bg-emerald-700 text-xs disabled:opacity-50">Approve</button>
                      <button onClick={() => applyAction(row.id, "rejected")} disabled={actionLoading} className="px-2 py-1 rounded bg-rose-700 text-xs disabled:opacity-50">Reject</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 bg-black/70 p-4 md:p-8 flex items-center justify-center">
          <div className="w-full max-w-4xl rounded-xl border border-slate-700 bg-[#0d1520] p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">{selected.doc_type}</h2>
                <p className="text-sm text-slate-400 mt-1">{selected.id} | {selected.institution}</p>
              </div>
              <button onClick={() => setSelected(null)} className="px-3 py-1 rounded bg-slate-700 text-sm">Close</button>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mt-4">
              <div className="md:col-span-2 space-y-4">
                <section className="rounded-lg border border-slate-700 bg-slate-900/30 p-3">
                  <h3 className="text-sm font-semibold mb-2">Extracted Fields</h3>
                  <pre className="text-xs text-slate-300 whitespace-pre-wrap">{JSON.stringify(selected.extracted_fields || {}, null, 2)}</pre>
                </section>

                <section className="rounded-lg border border-slate-700 bg-slate-900/30 p-3">
                  <h3 className="text-sm font-semibold mb-2">AI Flags</h3>
                  {selected.flags?.length ? (
                    <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">
                      {selected.flags.map((flag) => <li key={flag}>{flag}</li>)}
                    </ul>
                  ) : (
                    <p className="text-sm text-slate-400">No flags.</p>
                  )}
                </section>
              </div>

              <aside className="space-y-3">
                <section className="rounded-lg border border-slate-700 bg-slate-900/30 p-3">
                  <div className="text-xs text-slate-400">DSS</div>
                  <div className="text-3xl font-bold mt-1">{selected.dss}</div>
                  <div className="mt-2"><StatusPill status={selected.status} /></div>
                </section>

                <section className="rounded-lg border border-slate-700 bg-slate-900/30 p-3">
                  <label className="text-sm font-semibold">Reviewer Notes</label>
                  <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    rows={4}
                    className="mt-2 w-full rounded bg-black/20 border border-slate-700 p-2 text-sm"
                    placeholder="Add notes for institution or audit trail"
                  />
                  <div className="grid grid-cols-1 gap-2 mt-3">
                    <button onClick={() => applyAction(selected.id, "approved")} disabled={actionLoading} className="px-3 py-2 rounded bg-emerald-700 text-sm disabled:opacity-50">Approve</button>
                    <button onClick={() => applyAction(selected.id, "rejected")} disabled={actionLoading} className="px-3 py-2 rounded bg-rose-700 text-sm disabled:opacity-50">Reject</button>
                    <button onClick={() => applyAction(selected.id, "request_correction")} disabled={actionLoading} className="px-3 py-2 rounded bg-amber-700 text-sm disabled:opacity-50">Request Correction</button>
                  </div>
                </section>
              </aside>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, tone = "slate" }) {
  const toneMap = {
    slate: "text-white",
    amber: "text-amber-300",
    red: "text-rose-300",
    cyan: "text-cyan-300",
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/35 p-4">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${toneMap[tone] || toneMap.slate}`}>{value}</div>
    </div>
  );
}
