import React, { useState } from "react";
import { Upload as UploadIcon, File, CheckCircle, AlertCircle, Loader } from "lucide-react";

export default function Upload() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleDrag = (e) => {
    e.preventDefault();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const newFiles = Array.from(e.dataTransfer.files);
    setFiles([...files, ...newFiles]);
  };

  const handleFileSelect = (e) => {
    setFiles([...files, ...Array.from(e.target.files)]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    // Simulate processing each file
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const processedFiles = files.map((file, idx) => ({
      id: Date.now() + idx,
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2),
      uploadedAt: new Date().toLocaleDateString(),
      status: "processed",
      dss: Math.floor(Math.random() * 40 + 60), // 60-100 DSS
    }));
    
    setUploadedFiles([...processedFiles, ...uploadedFiles]);
    setFiles([]);
    setUploading(false);
  };

  const removeFile = (idx) => {
    setFiles(files.filter((_, i) => i !== idx));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-primary rounded-lg">
              <UploadIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">Document Upload</h1>
          </div>
          <p className="text-slate-400">Upload institutional documents for compliance review and DSS scoring</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Area */}
          <div className="lg:col-span-2">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition ${
                dragActive
                  ? "border-primary bg-primary/10"
                  : "border-slate-600/40 bg-slate-800/20 hover:border-slate-500"
              }`}
            >
              <UploadIcon className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Drag & Drop Documents</h3>
              <p className="text-slate-400 mb-6">or click to select files</p>
              <input
                type="file"
                id="file-input"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept=".pdf,.doc,.docx,.xls,.xlsx"
              />
              <label
                htmlFor="file-input"
                className="inline-block px-8 py-3 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 text-white rounded-lg font-semibold cursor-pointer transition"
              >
                Browse Files
              </label>
              <p className="text-slate-500 text-sm mt-4">PDF, DOC, DOCX, XLS supported (Max 50MB)</p>
            </div>

            {/* Selected Files */}
            {files.length > 0 && (
              <div className="mt-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">
                  Ready to Upload ({files.length})
                </h3>
                <div className="space-y-3 mb-6">
                  {files.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-4 bg-slate-700/20 rounded-lg border border-slate-700/40 hover:border-slate-600/60 transition"
                    >
                      <div className="flex items-center gap-3">
                        <File className="w-5 h-5 text-primary" />
                        <div className="text-left">
                          <p className="text-slate-300 font-medium">{file.name}</p>
                          <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(idx)}
                        className="text-slate-500 hover:text-red-400 transition"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="w-full py-3 bg-gradient-primary hover:shadow-lg hover:shadow-primary/50 disabled:opacity-60 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <UploadIcon className="w-4 h-4" />
                      Upload All Files
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Uploaded Files History */}
            {uploadedFiles.length > 0 && (
              <div className="mt-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  Upload History ({uploadedFiles.length})
                </h3>
                <div className="space-y-3">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="p-4 bg-slate-700/20 rounded-lg border border-slate-700/40">
                      <div className="flex items-start justify-between">
                        <div className="flex gap-3 flex-1">
                          <div className="p-2 bg-green-500/20 rounded-lg h-fit">
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          </div>
                          <div>
                            <p className="text-slate-300 font-medium">{file.name}</p>
                            <p className="text-xs text-slate-500">{file.uploadedAt} • {file.size} MB</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-400">{file.dss}</p>
                          <p className="text-xs text-slate-500">DSS</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Info Sidebar */}
          <div className="space-y-6">
            <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Requirements
              </h3>
              <ul className="space-y-3 text-sm text-slate-400">
                <li className="flex gap-3">
                  <span className="text-green-400 flex-shrink-0">✓</span>
                  <span>Valid institutional documents</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-green-400 flex-shrink-0">✓</span>
                  <span>PDF, Word, or Excel format</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-green-400 flex-shrink-0">✓</span>
                  <span>Max 50 MB per file</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-green-400 flex-shrink-0">✓</span>
                  <span>Clear, readable content</span>
                </li>
              </ul>
            </div>

            <div className="bg-gradient-primary/10 border border-primary/30 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-400" />
                About DSS
              </h3>
              <p className="text-sm text-slate-300">
                Document Sufficiency Score (DSS) indicates the completeness and quality of your submission (0-100).
              </p>
            </div>

            <div className="bg-slate-700/20 border border-slate-700/40 rounded-xl p-6">
              <p className="text-sm text-slate-400">
                💡 Tip: Upload all mandatory documents together for accurate compliance verification.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


