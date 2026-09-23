"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  UploadCloud,
  FileCheck,
  AlertTriangle,
  Lock,
  Trash2,
  ShieldAlert,
  ArrowRight,
  FileText,
  CheckCircle,
  Binary,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { api } from "@/lib/api";
import { formatBytes, parseApiError } from "@/lib/utils";

export default function FileScannerPage() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [authorized, setAuthorized] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const allowedExtensions = [
    ".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".txt", ".json", ".xml", ".csv"
  ];

  const handleFileSelection = (selectedFile: File) => {
    setError("");
    const ext = "." + (selectedFile.name.split(".").pop()?.toLowerCase() || "");
    if (!allowedExtensions.includes(ext)) {
      setError(`File extension '${ext}' is not supported. Supported formats: ${allowedExtensions.join(", ")}`);
      return;
    }
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError("File exceeds maximum allowed limit of 50MB.");
      return;
    }
    setFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to scan.");
      return;
    }
    if (!authorized) {
      setError("You must confirm you are authorized to analyze this file.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.startFileScan(file, authorized);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setError(parseApiError(err, "Scanning failed. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <FileCheck className="w-3.5 h-3.5 text-[#71C9CE]" />
          <span>Static File Analysis • Engine 03</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Static File Security Scanner
        </h1>
        <p className="text-slate-400 text-sm sm:text-base mt-2 max-w-xl mx-auto leading-relaxed">
          Inspect file type, byte entropy, structural metadata, and embedded binary content without executing uploads.
        </p>
      </div>

      <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] shadow-2xl space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dropzone */}
          <div
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all ${
              dragActive
                ? "border-[#71C9CE] bg-[#131e2e] shadow-lg shadow-[#71C9CE]/10"
                : "border-[#1a293e] hover:border-[#71C9CE]/50 bg-[#070b12]"
            }`}
          >
            <div className="flex flex-col items-center justify-center space-y-3">
              <div className="w-12 h-12 rounded-xl bg-[#0d1522] border border-[#1a293e] flex items-center justify-center text-[#71C9CE]">
                <UploadCloud className="w-6 h-6 text-[#71C9CE]" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[#E3FDFD]">
                  Drag and drop your file here, or{" "}
                  <label className="text-[#71C9CE] hover:text-[#A6E3E9] cursor-pointer underline underline-offset-2">
                    browse files
                    <input
                      type="file"
                      className="hidden"
                      onChange={(e) => e.target.files && handleFileSelection(e.target.files[0])}
                    />
                  </label>
                </p>
                <p className="text-xs text-slate-500 font-mono">
                  Supported formats: PDF, DOCX, XLSX, PPTX, PNG, JPG, ZIP, JSON, XML (Max 50MB)
                </p>
              </div>
            </div>

            {/* Selected File Preview */}
            {file && (
              <div className="mt-6 p-4 rounded-xl bg-[#0d1522] border border-[#71C9CE]/40 flex items-center justify-between text-left font-mono">
                <div className="flex items-center gap-3 truncate">
                  <FileText className="w-5 h-5 text-[#71C9CE] shrink-0" />
                  <div className="truncate">
                    <p className="text-xs font-bold text-[#E3FDFD] truncate">{file.name}</p>
                    <p className="text-[11px] text-slate-400">{formatBytes(file.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="p-1.5 rounded-lg hover:bg-[#131e2e] text-slate-400 hover:text-red-400 transition"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="file-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-[#1a293e] text-[#71C9CE] focus:ring-0"
              />
              <label htmlFor="file-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer font-sans">
                <strong className="text-[#E3FDFD] font-mono">Authorization Affirmation:</strong> I confirm that I am authorized to upload and analyze this file. I understand files are inspected statically with zero execution and purged after analysis.
              </label>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40 text-red-300 text-xs flex items-center gap-3 font-mono">
              <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full py-3.5 rounded-xl bg-[#71C9CE] hover:bg-[#A6E3E9] text-[#070b12] font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-[#71C9CE]/25 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-[#070b12] border-t-transparent rounded-full animate-spin" />
                <span>Running Static Inspections...</span>
              </>
            ) : (
              <>
                <span>Run Static File Inspection</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Feature Highlights Grid */}
        <div className="mt-10 pt-8 border-t border-[#1a293e] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Binary className="w-4 h-4 text-[#71C9CE]" />
              <span>Byte Entropy Profiling</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Calculates Shannon entropy to detect packed, encrypted, or obfuscated payloads.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Layers className="w-4 h-4 text-[#71C9CE]" />
              <span>Archive Traversal Checks</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Detects Zip-Slip directory traversal attempts, recursive bombs, and double extensions.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Lock className="w-4 h-4 text-[#71C9CE]" />
              <span>Macro &amp; Script Detection</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Flags embedded JavaScript in PDFs and suspicious VBA macros inside documents.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <ShieldCheck className="w-4 h-4 text-[#71C9CE]" />
              <span>Zero-Execution Sandbox</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Files are evaluated purely as byte arrays and structured trees with zero runtime execution.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <FileCheck className="w-4 h-4 text-[#71C9CE]" />
              <span>Cryptographic Hashes</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Computes authoritative SHA-256 and MD5 hashes for verified file integrity tracking.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Trash2 className="w-4 h-4 text-[#71C9CE]" />
              <span>Automated Shredding</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Uploaded files are securely overwritten with pseudorandom bytes and permanently unlinked.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
