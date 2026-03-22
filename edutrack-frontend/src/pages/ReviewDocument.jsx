import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FileText, ArrowLeft, Check, X, AlertCircle } from "lucide-react";

export default function ReviewDocument() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [notes, setNotes] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const data = {
    id: id || "DOC-001",
    file_name: "fire_safety_certificate.pdf",
    institution: "North Valley Institute",
    upload_date: "2024-09-01",
    dss: 95,
    status: "needs_review",
    parsed_fields: {
      certificate_no: "FS-2024-0091",
      valid_till: "2027-09-01",
      authority: "City Fire Department",
      issued_date: "2024-09-01",
    },
    flags: [
      "Low OCR confidence on signature area",
      "Missing official seal (detected)",
      "Expiry date found and validated",
    ],
  };

  const handleApprove = async () => {
    setActionLoading(true);
    setTimeout(() => {
      setActionLoading(false);
      navigate(-1);
    }, 1000);
  };

  const handleReject = async () => {
    setActionLoading(true);
    setTimeout(() => {
      setActionLoading(false);
      navigate(-1);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-slate-400 hover:text-white mb-4 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">{data.file_name}</h1>
              <p className="text-slate-400 text-sm mt-1">
                {data.id} | {data.institution} | Uploaded {data.upload_date}
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document Preview */}
          <div className="lg:col-span-2 bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Document Preview</h3>
            <div className="w-full h-96 bg-slate-900/50 border border-slate-700/40 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <FileText className="w-16 h-16 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">PDF preview unavailable in demo mode</p>
                <p className="text-xs text-slate-500 mt-1">Download to view full document</p>
              </div>
            </div>
          </div>

          {/* DSS & Actions */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6 flex flex-col">
            <div className="mb-6">
              <p className="text-slate-400 text-sm mb-2">Document Sufficiency Score</p>
              <div className="text-5xl font-bold text-primary mb-2">{data.dss}</div>
              <div className="w-full bg-slate-700/30 rounded-full h-2">
                <div
                  className="bg-gradient-primary h-2 rounded-full"
                  style={{ width: `${data.dss}%` }}
                ></div>
              </div>
              <p className="text-xs text-slate-500 mt-2">High confidence</p>
            </div>

            <div className="flex-1">
              <label className="text-sm font-semibold text-white block mb-2">Reviewer Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add your review notes and observations..."
                className="w-full h-40 bg-slate-900/30 border border-slate-700/40 rounded-lg p-3 text-sm text-white placeholder-slate-500 resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 mt-6">
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                Approve
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition disabled:opacity-50"
              >
                <X className="w-4 h-4" />
                Reject
              </button>
            </div>
          </div>
        </div>

        {/* Extracted Fields & Flags */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Extracted Fields */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Extracted Fields</h3>
            <div className="space-y-3">
              {Object.entries(data.parsed_fields).map(([key, value]) => (
                <div key={key} className="flex justify-between items-start p-3 bg-slate-900/30 rounded-lg border border-slate-700/20">
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wide">{key.replace(/_/g, " ")}</p>
                    <p className="text-white font-medium mt-1">{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Flags */}
          <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              AI Flags & Observations
            </h3>
            <div className="space-y-3">
              {data.flags.map((flag, idx) => (
                <div key={idx} className="flex gap-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0"></div>
                  <p className="text-sm text-yellow-100">{flag}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
