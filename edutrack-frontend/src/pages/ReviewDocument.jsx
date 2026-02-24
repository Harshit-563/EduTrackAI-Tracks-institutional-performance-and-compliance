import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function ReviewDocument() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [notes, setNotes] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    setData({
      id,
      file_name: "fire_safety_certificate.pdf",
      institution: "North College",
      upload_date: "2024-09-01",
      dss: 95,
      parsed_fields: { valid_till: "2027-09-01" },
      flags: ["Low OCR confidence on signature area", "Missing official seal (detected)"],
    });
  }, [id]);

  if (!data) return <div className="p-6 text-gray-300">Loading document...</div>;

  return (
    <div className="min-h-screen bg-[#0b1620] text-gray-200 px-8 py-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-semibold">{data.file_name} - {data.institution}</h2>
          <p className="text-gray-400 text-sm">{data.id} | Uploaded: {data.upload_date}</p>
        </div>
        <button onClick={() => navigate(-1)} className="px-4 py-2 bg-gray-800 rounded">Back</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="border border-gray-800 rounded p-4 bg-gray-900/20">
          <h3 className="font-semibold mb-2">Document Preview</h3>
          <div className="h-72 bg-black/20 border border-gray-800 rounded flex items-center justify-center text-gray-400 text-sm">
            Preview unavailable in demo mode
          </div>
        </div>

        <div className="border border-gray-800 rounded p-4 bg-gray-900/20">
          <h3 className="font-semibold mb-2">Extracted Fields</h3>
          <pre className="text-sm bg-black/20 p-3 rounded border border-gray-800">{JSON.stringify(data.parsed_fields, null, 2)}</pre>
          <h3 className="font-semibold mt-4 mb-2">AI Flags</h3>
          <ul className="list-disc ml-4 text-sm">
            {data.flags.map((f) => <li key={f}>{f}</li>)}
          </ul>
        </div>

        <div className="border border-gray-800 rounded p-4 bg-gray-900/20">
          <div className="text-sm text-gray-400">DSS</div>
          <div className="text-4xl font-bold mb-4">{data.dss}</div>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Reviewer notes" className="w-full h-28 bg-black/20 border border-gray-700 rounded p-2 text-sm" />
          <div className="flex gap-2 mt-4">
            <button className="px-3 py-2 bg-green-600 rounded">Approve</button>
            <button className="px-3 py-2 bg-red-600 rounded">Reject</button>
          </div>
        </div>
      </div>
    </div>
  );
}
