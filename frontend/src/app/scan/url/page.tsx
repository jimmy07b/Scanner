"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Radio,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  Lock,
  ExternalLink,
  Fingerprint,
  Link as LinkIcon,
  ShieldCheck,
} from "lucide-react";
import { api } from "@/lib/api";
import { parseApiError } from "@/lib/utils";

export default function UrlCheckPage() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [authorized, setAuthorized] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError("Please enter a valid link or URL to check.");
      return;
    }
    if (!authorized) {
      setError("You must confirm you have authorization to check this link.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.startUrlCheck(url.trim(), authorized);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setError(
        parseApiError(err, "URL check failed. Verify the URL format and try again.")
      );
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <Radio className="w-3.5 h-3.5 text-[#71C9CE]" />
          <span>URL Threat Analysis • Engine 02</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          URL Threat &amp; Phishing Check
        </h1>
        <p className="text-slate-400 text-sm sm:text-base mt-2 max-w-xl mx-auto leading-relaxed">
          Inspect redirect behavior, domain deception, phishing indicators, and virus payload links using live response telemetry.
        </p>
      </div>

      <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] shadow-2xl space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-[#CBF1F5] uppercase tracking-wider font-mono">
              Suspicious URL or Link to Check
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <LinkIcon className="w-5 h-5 text-[#71C9CE]" />
              </div>
              <input
                type="text"
                placeholder="e.g. https://paypal-security-verify.com/login or bit.ly/target"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] placeholder-slate-500 text-sm focus:outline-none focus:border-[#71C9CE] transition"
              />
            </div>
          </div>

          {/* Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="url-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-[#1a293e] text-[#71C9CE] focus:ring-0"
              />
              <label htmlFor="url-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer font-sans">
                <strong className="text-[#E3FDFD] font-mono">Authorization Affirmation:</strong> I confirm that I am checking this link for legitimate security evaluation or verification purposes.
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
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-[#71C9CE] hover:bg-[#A6E3E9] text-[#070b12] font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-[#71C9CE]/25 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-[#070b12] border-t-transparent rounded-full animate-spin" />
                <span>Tracing Redirection &amp; Link Risk...</span>
              </>
            ) : (
              <>
                <span>Run URL Threat Check</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Threat Inspection Breakdown Grid */}
        <div className="mt-10 pt-8 border-t border-[#1a293e] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <ShieldAlert className="w-4 h-4 text-[#71C9CE]" />
              <span>Brand Impersonation</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Identifies deceptive lookalike domains targeting PayPal, Apple, Google, Microsoft, and banks.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <ExternalLink className="w-4 h-4 text-[#71C9CE]" />
              <span>Redirection Journey</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Tracks every HTTP 301/302 hop, uncovering final landing destinations across cross-domain redirects.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Fingerprint className="w-4 h-4 text-[#71C9CE]" />
              <span>Deception Heuristics</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Detects raw numeric IP hosts, internationalized punycode spoofing (xn--), and authority @ tricks.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <ShieldCheck className="w-4 h-4 text-[#71C9CE]" />
              <span>Malware Payload Links</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Inspects query targets for direct executable file deliveries (.exe, .msi, .bat, .apk).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Lock className="w-4 h-4 text-[#71C9CE]" />
              <span>Credential Form Theft</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Audits password input presence on unencrypted or unauthenticated third-party domains.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Radio className="w-4 h-4 text-[#71C9CE]" />
              <span>Live Telemetry</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Captures actual response HTTP status, latency, server headers, and certificate parameters.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
