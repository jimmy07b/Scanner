"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Globe,
  Radio,
  FileSearch,
  ArrowRight,
  Shield,
  Lock,
  CheckCircle2,
  Clock,
  Upload,
} from "lucide-react";
import { api } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();

  // Active Scanner Tab: "website" (Primary) | "url" | "file"
  const [activeEngine, setActiveEngine] = useState<"website" | "url" | "file">("website");

  // Website Audit State
  const [siteInput, setSiteInput] = useState("");
  const [siteLoading, setSiteLoading] = useState(false);
  const [siteError, setSiteError] = useState("");

  // URL Check State
  const [urlInput, setUrlInput] = useState("");
  const [urlLoading, setUrlLoading] = useState(false);
  const [urlError, setUrlError] = useState("");

  // File Scanner State
  const [dragActive, setDragActive] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState("");

  const parseError = (err: any, fallback: string): string => {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
    }
    if (err.message && (err.message.includes("Network Error") || err.code === "ERR_NETWORK")) {
      return "Backend service is establishing connection / waking up. Please retry in 10-15 seconds.";
    }
    return err.message || fallback;
  };

  // Handle Website Audit
  const handleWebsiteAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteInput.trim()) {
      setSiteError("Please enter a valid website domain or URL.");
      return;
    }
    setSiteLoading(true);
    setSiteError("");
    try {
      const res = await api.startWebsiteAudit(siteInput.trim(), true);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setSiteError(parseError(err, "Website audit failed. Please retry in a few moments."));
      setSiteLoading(false);
    }
  };

  // Handle URL Check
  const handleUrlCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) {
      setUrlError("Please enter a valid URL to inspect.");
      return;
    }
    setUrlLoading(true);
    setUrlError("");
    try {
      const res = await api.startUrlCheck(urlInput.trim(), true);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setUrlError(parseError(err, "URL check failed. Please check the input and retry."));
      setUrlLoading(false);
    }
  };

  // Handle File Upload
  const handleFileUpload = async (file: File) => {
    setFileError("");
    const ext = "." + (file.name.split(".").pop()?.toLowerCase() || "");
    if (ext === ".crdownload" || ext === ".tmp" || ext === ".part") {
      setFileError(
        `The file '${file.name}' is an incomplete download (${ext}). Please wait for download completion.`
      );
      return;
    }
    const dangerousBlocked = [".exe", ".bat", ".cmd", ".sh", ".vbs", ".ps1", ".msi", ".com"];
    if (dangerousBlocked.includes(ext)) {
      setFileError(
        `Direct upload of raw executable binaries (${ext}) is blocked for safety. Please submit inside a .zip archive for static structural inspection.`
      );
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setFileError("File exceeds the maximum allowed size limit of 50MB.");
      return;
    }

    setFileLoading(true);
    try {
      const res = await api.startFileScan(file, true);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setFileError(parseError(err, "File scan failed. Ensure file is within size limits."));
      setFileLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between selection:bg-blue-500/20 selection:text-blue-200">
      
      {/* Centered Minimal Hero & Scanner Workstation */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 w-full text-center my-auto">

        {/* Clear Headline */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.15] mb-4">
          Precision Security Analysis
        </h1>

        {/* Short Subtitle */}
        <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto font-normal leading-relaxed mb-8">
          Analyze live websites, suspicious URLs, and uploaded files with structured, evidence-based checks.
        </p>

        {/* Hero Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
          <button
            type="button"
            onClick={() => {
              setActiveEngine("website");
              const el = document.getElementById("website-input");
              if (el) el.focus();
            }}
            className="px-5 py-2.5 rounded-lg bg-[#71C9CE] hover:bg-[#A6E3E9] text-[#070b12] text-xs sm:text-sm font-bold shadow-lg shadow-[#71C9CE]/25 transition flex items-center gap-2"
          >
            <Globe className="w-4 h-4 text-[#070b12]" />
            <span>Start Website Audit</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveEngine("url");
              const el = document.getElementById("url-input");
              if (el) el.focus();
            }}
            className="px-5 py-2.5 rounded-lg bg-[#0d1522] hover:bg-[#131e2e] text-[#CBF1F5] hover:text-[#E3FDFD] border border-[#1a293e] hover:border-[#71C9CE] text-xs sm:text-sm font-medium transition flex items-center gap-2"
          >
            <Radio className="w-4 h-4 text-[#71C9CE]" />
            <span>Run URL Check</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveEngine("file");
              const el = document.getElementById("file-upload-input");
              if (el) el.click();
            }}
            className="px-5 py-2.5 rounded-lg bg-[#0d1522] hover:bg-[#131e2e] text-[#CBF1F5] hover:text-[#E3FDFD] border border-[#1a293e] hover:border-[#71C9CE] text-xs sm:text-sm font-medium transition flex items-center gap-2"
          >
            <FileSearch className="w-4 h-4 text-[#71C9CE]" />
            <span>Scan File</span>
          </button>
        </div>

        {/* Scanner Section Title & Description */}
        <div className="text-left mb-4" id="engines">
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Security Engines
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Three focused analysis engines for website posture, link risk, and static file inspection.
          </p>
        </div>

        {/* Focused Scanner Box */}
        <div className="rounded-2xl border border-[#1a293e] bg-[#0d1522] p-6 sm:p-8 text-left shadow-2xl">
          
          {/* Engine Selector Tabs */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-6 border-b border-[#1a293e]">
            <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-lg bg-[#070b12] border border-[#1a293e]">
              
              {/* Tab 1: Website Security Audit */}
              <button
                type="button"
                onClick={() => setActiveEngine("website")}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 ${
                  activeEngine === "website"
                    ? "bg-[#131e2e] text-[#E3FDFD] border border-[#71C9CE]/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Globe className="w-3.5 h-3.5 text-[#71C9CE]" />
                <span>Website Security Audit</span>
              </button>

              {/* Tab 2: URL Threat Check */}
              <button
                type="button"
                onClick={() => setActiveEngine("url")}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 ${
                  activeEngine === "url"
                    ? "bg-[#131e2e] text-[#E3FDFD] border border-[#71C9CE]/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Radio className="w-3.5 h-3.5 text-[#71C9CE]" />
                <span>URL Threat Check</span>
              </button>

              {/* Tab 3: Static File Scanner */}
              <button
                type="button"
                onClick={() => setActiveEngine("file")}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-colors flex items-center gap-2 ${
                  activeEngine === "file"
                    ? "bg-[#131e2e] text-[#E3FDFD] border border-[#71C9CE]/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileSearch className="w-3.5 h-3.5 text-[#71C9CE]" />
                <span>Static File Scanner</span>
              </button>
            </div>
          </div>

          {/* Tab 1 Content: Website Security Audit */}
          {activeEngine === "website" && (
            <div className="pt-6 space-y-4">
              <div>
                <h3 className="text-base font-semibold text-white">
                  Live Website Security Audit
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Review HTTPS configuration, response headers, cookie handling, exposed metadata, and technology fingerprints from the live target.
                </p>
              </div>

              <form onSubmit={handleWebsiteAudit} className="flex flex-col sm:flex-row gap-3">
                <input
                  id="website-input"
                  type="text"
                  placeholder="Enter domain or URL (e.g. example.com or https://target.com)"
                  value={siteInput}
                  onChange={(e) => setSiteInput(e.target.value)}
                  disabled={siteLoading}
                  className="flex-1 text-sm px-4 py-3 rounded-lg bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] placeholder-slate-500 focus:outline-none focus:border-[#71C9CE] transition-colors disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={siteLoading}
                  className="px-6 py-3 rounded-lg bg-[#71C9CE] hover:bg-[#A6E3E9] disabled:opacity-50 text-[#070b12] text-sm font-bold shadow-md shadow-[#71C9CE]/25 transition-colors flex items-center justify-center gap-2 shrink-0"
                >
                  {siteLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-[#070b12] border-t-transparent rounded-full animate-spin" />
                      <span>Auditing...</span>
                    </>
                  ) : (
                    <>
                      <span>Start Website Audit</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* Quick Test Chips */}
              <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                <span className="text-[11px] font-mono text-slate-500">Test Target:</span>
                {["example.com", "cloudflare.com", "github.com"].map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    onClick={() => setSiteInput(sample)}
                    className="px-2.5 py-1 rounded-md bg-[#090d16] hover:bg-slate-800 border border-slate-800 text-[11px] font-mono text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    {sample}
                  </button>
                ))}
              </div>

              {siteError && (
                <div className="p-3 rounded-lg bg-red-950/20 border border-red-800/40 text-xs text-red-300">
                  {siteError}
                </div>
              )}
            </div>
          )}

          {/* Tab 2 Content: URL Threat Check */}
          {activeEngine === "url" && (
            <div className="pt-6 space-y-4">
              <div>
                <h3 className="text-base font-semibold text-white">
                  URL Threat Analysis
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Inspect redirect behavior, domain structure, and phishing indicators using live response data.
                </p>
              </div>

              <form onSubmit={handleUrlCheck} className="flex flex-col sm:flex-row gap-3">
                <input
                  id="url-input"
                  type="text"
                  placeholder="https://example.com/login"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  disabled={urlLoading}
                  className="flex-1 text-sm px-4 py-3 rounded-lg bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] placeholder-slate-500 focus:outline-none focus:border-[#71C9CE] transition-colors disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={urlLoading}
                  className="px-6 py-3 rounded-lg bg-[#71C9CE] hover:bg-[#A6E3E9] disabled:opacity-50 text-[#070b12] text-sm font-bold shadow-md shadow-[#71C9CE]/25 transition-colors flex items-center justify-center gap-2 shrink-0"
                >
                  {urlLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-[#070b12] border-t-transparent rounded-full animate-spin" />
                      <span>Checking...</span>
                    </>
                  ) : (
                    <>
                      <span>Run URL Check</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {urlError && (
                <div className="p-3 rounded-lg bg-red-950/20 border border-red-800/40 text-xs text-red-300">
                  {urlError}
                </div>
              )}
            </div>
          )}

          {/* Tab 3 Content: Static File Scanner */}
          {activeEngine === "file" && (
            <div className="pt-6 space-y-4">
              <div>
                <h3 className="text-base font-semibold text-white">
                  Static File Analysis
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Inspect file type, metadata, structure, and embedded content without executing uploads.
                </p>
              </div>

              <label
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                className={`cursor-pointer block text-center py-8 px-4 rounded-xl border border-dashed transition-all text-xs ${
                  dragActive
                    ? "border-[#71C9CE] bg-[#131e2e] text-[#E3FDFD] shadow-lg shadow-[#71C9CE]/10"
                    : "border-[#1a293e] hover:border-[#71C9CE]/60 bg-[#070b12] text-slate-400 hover:text-[#CBF1F5]"
                }`}
              >
                <input
                  id="file-upload-input"
                  type="file"
                  className="hidden"
                  onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                  disabled={fileLoading}
                />
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-full bg-[#0d1522] border border-[#1a293e] flex items-center justify-center text-[#71C9CE]">
                    <Upload className="w-5 h-5 text-[#71C9CE]" />
                  </div>
                  <div className="space-y-0.5">
                    <p className="font-semibold text-[#E3FDFD]">
                      Click to upload or drag &amp; drop archive
                    </p>
                    <p className="text-slate-500 text-[11px]">
                      Safe static structure analysis (ZIP, tar, docs up to 50MB)
                    </p>
                  </div>
                </div>
              </label>

              {fileError && (
                <div className="p-3 rounded-lg bg-red-950/20 border border-red-800/40 text-xs text-red-300">
                  {fileError}
                </div>
              )}
            </div>
          )}

        </div>

      </main>

    </div>
  );
}
