"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Radio,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  Lock,
  Search,
  CheckCircle2,
  ExternalLink,
  Fingerprint,
  Link as LinkIcon,
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Radio className="w-3.5 h-3.5" />
          <span>URL Threat Check</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          URL Threat Analysis
        </h1>
        <p className="text-zinc-400 text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Inspect redirect behavior, domain structure, and phishing indicators using live response data.
        </p>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Suspicious URL or Link to Check
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <LinkIcon className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="e.g. https://paypal-security-verify.com/login or bit.ly/target"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 transition"
              />
            </div>
          </div>

          {/* Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="url-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-slate-700 text-slate-200 focus:ring-0"
              />
              <label htmlFor="url-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer">
                <strong>Authorization Affirmation:</strong> I confirm that I am checking this link for legitimate security evaluation or verification purposes.
              </label>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-3">
              <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-slate-100 hover:bg-white text-slate-900 font-bold text-sm flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                <span>Queuing URL Analysis Pipeline...</span>
              </>
            ) : (
              <>
                <span>Run URL Check</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Feature Highlights Grid */}
        <div className="mt-10 pt-8 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <ShieldAlert className="w-4 h-4 text-slate-400" />
              <span>Brand Impersonation</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Detects typosquatted and lookalike domains targeting PayPal, Apple, Google, Microsoft, and banks.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Fingerprint className="w-4 h-4 text-slate-400" />
              <span>URL Obfuscation</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Flags deceptive userinfo <code className="text-slate-300">@</code> signs, raw numerical IP hostnames, and punycode.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <ExternalLink className="w-4 h-4 text-slate-400" />
              <span>Redirect Chain Tracking</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Safely follows HTTP redirects, detecting cross-domain forwarding and redirect cloaking.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
