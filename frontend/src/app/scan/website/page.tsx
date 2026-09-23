"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Globe,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Lock,
  Search,
  CheckCircle2,
  Server,
  FileText,
  Cookie,
  Sparkles,
  Layers,
} from "lucide-react";
import { api } from "@/lib/api";
import { parseApiError } from "@/lib/utils";

export default function WebsiteAuditPage() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [authorized, setAuthorized] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError("Please enter a valid website URL or domain.");
      return;
    }
    if (!authorized) {
      setError("You must confirm you own or are authorized to audit this target website.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.startWebsiteAudit(url.trim(), authorized);
      router.push(`/reports/${res.scan_id}`);
    } catch (err: any) {
      setError(
        parseApiError(err, "Website audit failed. Please check the URL and try again.")
      );
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Globe className="w-3.5 h-3.5" />
          <span>Website Security Audit • Core</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Live Website Security Audit
        </h1>
        <p className="text-zinc-400 text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Review HTTPS configuration, response headers, cookie handling, exposed metadata, and technology fingerprints from the live target.
        </p>
      </div>

      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Target Website Domain or URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <Globe className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="e.g. example.com or https://yourcompany.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 transition"
              />
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
              <span className="text-[11px] text-slate-500">
                Accepts domain (<code className="text-slate-400">mysite.io</code>) or full URL (<code className="text-slate-400">https://mysite.io</code>).
              </span>
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-400">
                <span className="text-slate-500">Quick Test:</span>
                {["example.com", "cloudflare.com", "github.com"].map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setUrl(chip)}
                    className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Authorization Checkbox */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="site-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-slate-700 text-slate-200 focus:ring-0"
              />
              <label htmlFor="site-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer">
                <strong>Authorization Affirmation:</strong> I confirm that I own or have received explicit written permission to audit this website. I understand RootLayer performs non-invasive passive HTTP requests only.
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
                <span>Dispatching Audit Pipeline...</span>
              </>
            ) : (
              <>
                <span>Start Website Security Audit</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Feature Highlights Grid */}
        <div className="mt-10 pt-8 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Server className="w-4 h-4 text-slate-400" />
              <span>6 Security Headers</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              HSTS, CSP, X-Frame-Options, X-Content-Type, Referrer-Policy, Permissions-Policy.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Cookie className="w-4 h-4 text-slate-400" />
              <span>Cookie Protection</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Audits Secure, HttpOnly, and SameSite attribute flags on all Set-Cookie headers.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Layers className="w-4 h-4 text-slate-400" />
              <span>Tech Stack Fingerprint</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Wappalyzer-style categorization for CMS, frameworks, servers, runtimes, and CDNs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <FileText className="w-4 h-4 text-slate-400" />
              <span>Sensitive Route Discovery</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Inspects robots.txt for leaked admin, backup, or staging endpoints.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Lock className="w-4 h-4 text-slate-400" />
              <span>TLS &amp; HTTPS Enforcement</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Verifies plain HTTP to encrypted HTTPS auto-redirects across all request history.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <ShieldCheck className="w-4 h-4 text-slate-400" />
              <span>HTML Form Hygiene</span>
            </div>
            <p className="text-slate-400 text-[11px]">
              Audits form action endpoints, plain HTTP targets, and anti-CSRF protection tokens.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
