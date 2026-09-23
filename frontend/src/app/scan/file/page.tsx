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
} from "lucide-react";
import { api } from "@/lib/api";
import { formatBytes } from "@/lib/utils";

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
    const ext = "." + selectedFile.name.split(".").pop()?.toLowerCase();
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
      setError(err.response?.data?.detail || "Scanning failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <FileCheck className="w-3.5 h-3.5" />
          <span>Static File Scanner</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Static File Analysis
        </h1>
        <p className="text-zinc-400 text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Inspect file type, metadata, structure, and embedded content without executing uploads.
        </p>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dropzone */}
          <div
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center transition-all ${
              dragActive
                ? "border-slate-500 bg-slate-900/60"
                : file
                ? "border-slate-600 bg-slate-900/40"
                : "border-slate-700 bg-slate-900/40 hover:border-slate-600"
            }`}
          >
            <input
              type="file"
              id="file-scan-input"
              className="hidden"
              onChange={(e) => e.target.files && handleFileSelection(e.target.files[0])}
              disabled={loading}
            />

            {file ? (
              <div className="space-y-3">
                <div className="w-14 h-14 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200 mx-auto">
                  <CheckCircle className="w-7 h-7" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-white break-all">{file.name}</h4>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{formatBytes(file.size)}</p>
                </div>
                <label
                  htmlFor="file-scan-input"
                  className="inline-block text-xs font-semibold text-slate-300 hover:text-white hover:underline cursor-pointer"
                >
                  Choose a different file
                </label>
              </div>
            ) : (
              <label
                htmlFor="file-scan-input"
                className="cursor-pointer flex flex-col items-center justify-center space-y-3"
              >
                <div className="w-14 h-14 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
                  <UploadCloud className="w-7 h-7" />
                </div>
                <div>
                  <span className="text-sm font-semibold text-slate-200 hover:text-white transition">
                    Click to browse your computer
                  </span>
                  <span className="text-sm text-slate-400"> or drag and drop here</span>
                </div>
                <p className="text-xs text-slate-400">
                  PDF, DOCX, XLSX, PPTX, PNG, JPG, WEBP, ZIP, TXT (Up to 50MB)
                </p>
              </label>
            )}
          </div>

          {/* Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="file-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-slate-700 text-slate-200 focus:ring-0"
              />
              <label htmlFor="file-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer">
                <strong>Authorization &amp; Privacy Confirmation:</strong> I confirm that I own or am legally authorized to assess this file. I understand this tool conducts safe static inspection only and will automatically shred the file within 24 hours.
              </label>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-400 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Submit CTA */}
          <button
            type="submit"
            disabled={!file || loading}
            className="w-full py-3.5 rounded-xl bg-slate-100 hover:bg-white text-slate-900 font-bold text-sm flex items-center justify-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                <span>Running Static Analysis Engines...</span>
              </>
            ) : (
              <>
                <span>Start Free Static Scan</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Security Footnote */}
        <div className="mt-8 pt-6 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center sm:text-left text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-slate-400 shrink-0" />
            <span>Zero code execution guarantee</span>
          </div>
          <div className="flex items-center gap-2">
            <Trash2 className="w-4 h-4 text-slate-400 shrink-0" />
            <span>24h automatic file shredder</span>
          </div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-slate-400 shrink-0" />
            <span>Multi-hash cryptographic audit</span>
          </div>
        </div>
      </div>
    </div>
  );
}
