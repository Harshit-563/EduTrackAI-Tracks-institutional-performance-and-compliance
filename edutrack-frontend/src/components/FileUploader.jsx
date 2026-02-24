import React, { useCallback, useRef, useState } from "react";
import client from "../api/api";

export default function FileUploader({ onResult }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onPick = useCallback((e) => {
    const chosen = e.target.files?.[0];
    setError("");
    setFile(chosen || null);
  }, []);

  async function upload() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const resp = await client.post("/upload-analyze", form);
      onResult?.(resp.data || {});
    } catch (err) {
      setError(err?.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border border-dashed border-gray-700 rounded-lg p-4">
      <div className="text-sm text-gray-300 mb-3">Select a PDF/JPG/PNG for analysis.</div>
      <div className="flex items-center gap-3">
        <input ref={inputRef} type="file" onChange={onPick} className="text-sm" />
        <button onClick={upload} disabled={!file || loading} className="px-3 py-2 bg-emerald-600 rounded disabled:opacity-50">
          {loading ? "Uploading..." : "Upload"}
        </button>
      </div>
      {file && <div className="text-xs text-gray-400 mt-2">{file.name}</div>}
      {error && <div className="text-sm text-red-400 mt-2">{error}</div>}
    </div>
  );
}
