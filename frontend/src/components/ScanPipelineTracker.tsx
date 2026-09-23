"use client";

import React, { useState } from "react";
import {
  FileSearch,
  Globe,
  Radio,
  CheckCircle2,
  Terminal,
  X,
  ShieldCheck,
} from "lucide-react";

interface ScanPipelineTrackerProps {
  scanType?: string;
  target?: string;
  stage?: string;
  progress?: number;
  status?: string;
}

const STAGES = [
  { key: "queued", label: "Queued", desc: "Queued in assessment pipeline", detail: "Initializing telemetry workers and allocating isolated worker environment." },
  { key: "fetching", label: "Connect", desc: "Network stream & TLS handshake", detail: "Establishing encrypted socket and extracting certificate chain parameters." },
  { key: "recon", label: "Recon", desc: "DNS, certificates & headers", detail: "Resolving A/AAAA/MX/TXT records and harvesting HTTP response headers." },
  { key: "analyzing", label: "Verification", desc: "Evaluating OWASP & surface posture", detail: "Auditing HSTS, CSP, cookie security flags, and configuration paths." },
  { key: "extracting", label: "Extraction", desc: "Parsing confirmed technical evidence", detail: "Fingerprinting web server, reverse proxies, and CMS technology profiles." },
  { key: "scoring", label: "Evaluation", desc: "Deterministic heuristic evaluation", detail: "Verifying observations against strict evidence-only baseline rules." },
  { key: "completed", label: "Finalized", desc: "Security assessment report ready", detail: "Rendering verified findings and passive telemetry write-up." },
];

export const ScanPipelineTracker: React.FC<ScanPipelineTrackerProps> = ({
  scanType = "website",
  target = "Target",
  stage = "queued",
  progress = 10,
  status = "running",
}) => {
  const [showInfo, setShowInfo] = useState(false);

  const normalizedStage = stage === "done" ? "completed" : stage;
  const currentStageIndex = STAGES.findIndex((s) => s.key === normalizedStage);
  const activeIndex = currentStageIndex === -1 ? 0 : currentStageIndex;
  const progressPercent = Math.min(100, Math.max(8, progress || 8));

  // Determine active stage object
  const activeStageObj = STAGES[activeIndex] || STAGES[0];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-6 font-sans text-slate-300">
      
      {/* 1. HEADER CARD WITH TARGET & '!' INFO BUTTON */}
      <div className="rounded-2xl border border-[#1a293e] bg-[#0d1522] p-6 space-y-4 shadow-xl">
        
        {/* Top Tag & Action Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 font-mono">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#070b12] text-[#CBF1F5] border border-[#1a293e] text-xs">
            {scanType === "file" ? (
              <FileSearch className="w-3.5 h-3.5 text-[#71C9CE]" />
            ) : scanType === "url_check" || scanType === "url" ? (
              <Radio className="w-3.5 h-3.5 text-[#71C9CE]" />
            ) : (
              <Globe className="w-3.5 h-3.5 text-[#71C9CE]" />
            )}
            <span className="font-semibold uppercase tracking-wider text-[11px]">
              {scanType === "file"
                ? "Static File Assessment"
                : scanType === "url_check" || scanType === "url"
                ? "URL Threat Analysis"
                : "Web Security Assessment"}
            </span>
          </div>

          {/* Interactive '!' Information Button */}
          <button
            type="button"
            onClick={() => setShowInfo(!showInfo)}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#070b12] hover:bg-[#131e2e] text-[#CBF1F5] hover:text-[#E3FDFD] border border-[#1a293e] hover:border-[#71C9CE] text-xs transition"
            title="Click to view scan capabilities & scope"
          >
            <span className="w-4 h-4 rounded-full bg-[#71C9CE]/20 text-[#71C9CE] flex items-center justify-center font-bold text-[10px]">
              !
            </span>
            <span>Inspection Scope</span>
          </button>
        </div>

        {/* Target Title & Evidence Baseline Subtitle */}
        <div className="space-y-1">
          <h1 className="text-xl sm:text-2xl font-bold text-white font-mono break-all tracking-tight">
            {target}
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Non-destructive passive telemetry • Evidence-first verification • Zero synthetic data
          </p>
        </div>

        {/* EXPANDABLE '!' INFORMATION NOTE */}
        {showInfo && (
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] text-xs font-sans text-slate-300 space-y-3 transition-all">
            <div className="flex items-center justify-between border-b border-[#1a293e] pb-2 font-mono">
              <div className="flex items-center gap-2 font-bold text-[#E3FDFD]">
                <span className="w-4 h-4 rounded-full bg-[#71C9CE]/20 text-[#71C9CE] flex items-center justify-center font-bold text-[10px]">
                  !
                </span>
                <span>Inspection Scope &amp; Safety Standard</span>
              </div>
              <button
                type="button"
                onClick={() => setShowInfo(false)}
                className="text-slate-400 hover:text-white text-xs flex items-center gap-1"
              >
                <X className="w-3.5 h-3.5" />
                <span>Close</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] leading-relaxed">
              <div className="space-y-0.5">
                <strong className="text-[#CBF1F5] block font-mono">1. Passive DNS &amp; Routing</strong>
                <p className="text-slate-400">
                  Inspects A/AAAA records, DMARC policy, SPF declarations, and CAA authorized issuers.
                </p>
              </div>

              <div className="space-y-0.5">
                <strong className="text-[#CBF1F5] block font-mono">2. TLS &amp; Transport Encryption</strong>
                <p className="text-slate-400">
                  Validates TLS protocol handshakes, cipher suite configuration, and certificate expiration.
                </p>
              </div>

              <div className="space-y-0.5">
                <strong className="text-[#CBF1F5] block font-mono">3. HTTP Defensive Directives</strong>
                <p className="text-slate-400">
                  Audits HSTS, Content-Security-Policy (CSP), X-Frame-Options, and Permissions-Policy.
                </p>
              </div>

              <div className="space-y-0.5">
                <strong className="text-[#CBF1F5] block font-mono">4. Technology &amp; CMS Profiling</strong>
                <p className="text-slate-400">
                  Passively fingerprints web servers, reverse proxies (Cloudflare, Nginx), CMS, and frameworks.
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-[#1a293e] text-[11px] text-slate-400 font-mono flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#71C9CE] shrink-0" />
              <span>
                100% Non-destructive passive analysis. No malicious exploit payloads or code execution.
              </span>
            </div>
          </div>
        )}

        {/* 2. PROGRESS ANIMATION */}
        <div className="pt-4 border-t border-[#1a293e] space-y-3 font-mono">
          
          {/* Progress Header: Stage Status + Percentage */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-200">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#71C9CE] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#71C9CE]"></span>
              </span>
              <span className="font-semibold uppercase tracking-wider text-[11px] text-[#CBF1F5]">
                {stage}
              </span>
              <span className="text-slate-400 font-sans text-xs sm:inline hidden">
                — {activeStageObj.desc}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-base sm:text-lg font-bold font-mono text-[#E3FDFD]">
                {progressPercent}%
              </span>
            </div>
          </div>

          {/* Precision Horizontal Progress Bar with Brand Cyan/Teal Sweep */}
          <div className="relative w-full h-2.5 rounded-full bg-[#070b12] overflow-hidden border border-[#1a293e]">
            <div
              className="h-full bg-gradient-to-r from-[#71C9CE] via-[#A6E3E9] to-[#E3FDFD] rounded-full transition-all duration-500 ease-out shadow-sm shadow-[#71C9CE]/30"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Subtitle / Active detail */}
          <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
            {activeStageObj.detail}
          </p>
        </div>

        {/* 3. TIMELINE PIPELINE STEPPER */}
        <div className="pt-4 border-t border-[#1a293e]">
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
            {STAGES.map((s, index) => {
              const isPast = index < activeIndex;
              const isCurrent = index === activeIndex;

              return (
                <div
                  key={s.key}
                  className={`p-2 rounded-lg border text-left transition-all ${
                    isCurrent
                      ? "bg-[#131e2e] border-[#71C9CE] text-[#E3FDFD] shadow-md shadow-[#71C9CE]/10"
                      : isPast
                      ? "bg-[#070b12] border-[#1a293e] text-slate-400"
                      : "bg-[#070b12]/50 border-[#1a293e]/50 text-slate-600"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`text-[9px] font-mono font-semibold ${
                        isCurrent
                          ? "text-[#A6E3E9]"
                          : isPast
                          ? "text-[#71C9CE]"
                          : "text-slate-600"
                      }`}
                    >
                      0{index + 1}
                    </span>
                    {isPast ? (
                      <CheckCircle2 className="w-3 h-3 text-[#71C9CE]" />
                    ) : isCurrent ? (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#E3FDFD] animate-pulse" />
                    ) : null}
                  </div>
                  <div
                    className={`text-[10px] font-mono font-medium truncate ${
                      isCurrent
                        ? "text-[#E3FDFD] font-semibold"
                        : isPast
                        ? "text-slate-300"
                        : "text-slate-500"
                    }`}
                  >
                    {s.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* 4. REAL-TIME AUDIT LOG ACTIVITY CONSOLE */}
      <div className="border border-[#1a293e] rounded-2xl bg-[#0d1522] p-4 space-y-2.5 font-mono text-xs shadow-xl">
        <div className="flex items-center justify-between text-slate-400 border-b border-[#1a293e] pb-2">
          <div className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-[#71C9CE]" />
            <span className="text-[11px] uppercase tracking-wider font-semibold text-[#CBF1F5]">
              Live Telemetry Stream
            </span>
          </div>
          <span className="text-[10px] text-slate-500">RootLayer ASVS Protocol</span>
        </div>

        <div className="space-y-1.5 text-[11px] text-slate-400">
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[01]</span>
            <span className={activeIndex >= 0 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Allocated isolated worker sandbox for target reconnaissance
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[02]</span>
            <span className={activeIndex >= 1 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Initiated TCP &amp; TLS 1.3 handshake negotiation
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[03]</span>
            <span className={activeIndex >= 2 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Harvesting passive DNS records (SPF, DMARC, CAA) and certificate chain
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[04]</span>
            <span className={activeIndex >= 3 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Inspecting HTTP headers, security cookies &amp; route surface policies
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[05]</span>
            <span className={activeIndex >= 4 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Fingerprinting web servers, CMS signatures, and technology stack
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#71C9CE] select-none">[06]</span>
            <span className={activeIndex >= 5 ? "text-[#E3FDFD]" : "text-slate-600"}>
              Finalizing evidence validation without synthetic or placeholder values
            </span>
          </div>
        </div>
      </div>

    </div>
  );
};
