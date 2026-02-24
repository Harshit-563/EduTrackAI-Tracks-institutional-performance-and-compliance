// src/pages/Upload.jsx
import React, { useState, useEffect } from "react";
import FileUploader from "../components/FileUploader";
import client from "../api/api";

export default function Upload() {
  const [uploadResult, setUploadResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Fetch previous submissions (mock fallback)
  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await client.get("/institutions/demo/submissions");

        if (Array.isArray(response.data)) {
          setHistory(response.data);
        } else {
          setHistory([]);
        }
      } catch (err) {
        console.warn("Backend history not found → using fallback data.");

        setHistory([
          {
            id: "H001",
            name: "fire_safety.pdf",
            uploaded_at: "2024-11-01",
            status: "parsed",
            dss: 92,
          },
          {
            id: "H002",
            name: "audit_report_2023.pdf",
            uploaded_at: "2024-10-12",
            status: "needs_review",
            dss: 55,
          },
        ]);
      } finally {
        setLoadingHistory(false);
      }
    }

    fetchHistory();
  }, []);

  // When FileUploader returns backend result
  function handleUpload(data) {
    setUploadResult(data);

    // Push into history visually
    setHistory((prev) => [
      {
        id: data?.submission_id || "new",
        name: data?.file_name || "uploaded_document.pdf",
        uploaded_at: new Date().toLocaleDateString(),
        status: "processing",
        dss: data?.dss || 0,
      },
      ...prev,
    ]);
  }

  return (
    <div className="min-h-screen text-gray-200 p-8 bg-[#0f1720]">

      <h1 className="text-3xl font-bold mb-2">Upload Documents</h1>
      <p className="text-gray-400 text-sm mb-6">
        Upload mandatory compliance documents. The AI engine will extract key fields and compute the Document Sufficiency Score (DSS).
      </p>

      {/* Upload box */}
      <div className="mb-10">
        <FileUploader onResult={handleUpload} />
      </div>

      {/* Result Panel */}
      {uploadResult && (
        <div className="bg-gray-900/20 border border-gray-800 rounded p-5 mb-10">

          <h2 className="text-xl font-semibold mb-4">Analysis Summary</h2>

          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 p-4 rounded border border-gray-700">
              <span className="text-gray-400 text-sm">DSS Score</span>
              <div className="text-3xl font-bold">{uploadResult.dss || "—"}</div>
            </div>

            <div className="bg-gray-800/50 p-4 rounded border border-gray-700">
              <span className="text-gray-400 text-sm">Compliance</span>
              <div className="text-3xl font-bold">{uploadResult.compliance || "—"}</div>
            </div>

            <div className="bg-gray-800/50 p-4 rounded border border-gray-700">
              <span className="text-gray-400 text-sm">Submission ID</span>
              <div className="text-xl">{uploadResult.submission_id || "—"}</div>
            </div>
          </div>

          {/* JSON extracted fields */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2 text-lg">Extracted Fields</h3>
            <pre className="p-3 bg-black/30 text-sm rounded overflow-auto max-h-64 border border-gray-700">
{JSON.stringify(uploadResult.extracted_fields || uploadResult.fields || {}, null, 2)}
            </pre>
          </div>

          {/* Flags */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2 text-lg">AI Flags</h3>
            <ul className="list-disc ml-5 text-gray-300 text-sm">
              {(uploadResult.flags || ["No issues detected"]).map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>

        </div>
      )}

      {/* Upload History */}
      <div>
        <h2 className="text-2xl font-bold mb-3">Recent Uploads</h2>

        <div className="bg-gray-900/10 border border-gray-800 p-4 rounded">
          {loadingHistory ? (
            <div className="text-gray-500 text-center py-6">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="text-gray-400 text-sm">No uploads yet.</div>
          ) : (
            <ul className="space-y-4">
              {history.map((item) => (
                <li key={item.id} className="flex justify-between items-center p-3 bg-gray-900/20 rounded border border-gray-800">
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-400">{item.uploaded_at}</div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-300">DSS: {item.dss}</span>

                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        item.status === "parsed"
                          ? "bg-green-700"
                          : item.status === "needs_review"
                          ? "bg-yellow-600"
                          : "bg-gray-700"
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

      </div>
    </div>
  );
}
