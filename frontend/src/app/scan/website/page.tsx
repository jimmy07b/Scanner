"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Globe,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Lock,
  Server,
  FileText,
  Cookie,
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
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <Globe className="w-3.5 h-3.5 text-[#71C9CE]" />
          <span>Website Security Audit • Engine 01</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Live Website Security Audit
        </h1>
        <p className="text-slate-400 text-sm sm:text-base mt-2 max-w-xl mx-auto leading-relaxed">
          Review HTTPS configuration, response headers, cookie handling, exposed metadata, and technology fingerprints from the live target.
        </p>
      </div>

      <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] shadow-2xl space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-[#CBF1F5] uppercase tracking-wider font-mono">
              Target Website Domain or URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <Globe className="w-5 h-5 text-[#71C9CE]" />
              </div>
              <input
                type="text"
                placeholder="e.g. example.com or https://yourcompany.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] placeholder-slate-500 text-sm focus:outline-none focus:border-[#71C9CE] transition"
              />
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
              <span className="text-[11px] text-slate-400">
                Accepts domain (<code className="text-[#A6E3E9]">mysite.io</code>) or full URL (<code className="text-[#A6E3E9]">https://mysite.io</code>).
              </span>
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-400">
                <span className="text-slate-500">Quick Test:</span>
                {["example.com", "cloudflare.com", "github.com"].map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setUrl(chip)}
                    className="px-2.5 py-0.5 rounded-md bg-[#070b12] hover:bg-[#131e2e] border border-[#1a293e] hover:border-[#71C9CE] text-[#CBF1F5] transition"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Authorization Affirmation Checkbox */}
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-2">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="site-auth-checkbox"
                checked={authorized}
                onChange={(e) => setAuthorized(e.target.checked)}
                className="mt-1 rounded border-[#1a293e] text-[#71C9CE] focus:ring-0"
              />
              <label htmlFor="site-auth-checkbox" className="text-xs text-slate-300 leading-relaxed cursor-pointer font-sans">
                <strong className="text-[#E3FDFD] font-mono">Authorization Affirmation:</strong> I confirm that I own or have received explicit written permission to audit this website. I understand RootLayer performs non-invasive passive HTTP requests only.
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
        <div className="mt-10 pt-8 border-t border-[#1a293e] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Server className="w-4 h-4 text-[#71C9CE]" />
              <span>6 Security Headers</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              HSTS, CSP, X-Frame-Options, X-Content-Type, Referrer-Policy, Permissions-Policy.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Cookie className="w-4 h-4 text-[#71C9CE]" />
              <span>Cookie Protection</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Audits Secure, HttpOnly, and SameSite attribute flags on all Set-Cookie headers.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Layers className="w-4 h-4 text-[#71C9CE]" />
              <span>Tech Stack Fingerprint</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Passive categorization for CMS, frameworks, servers, runtimes, and CDNs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <FileText className="w-4 h-4 text-[#71C9CE]" />
              <span>Sensitive Surfaces</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Inspects configuration endpoints for leaked admin, backup, or git directories.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <Lock className="w-4 h-4 text-[#71C9CE]" />
              <span>TLS &amp; Cipher Audit</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Verifies plain HTTP to encrypted HTTPS auto-redirects and cipher strength.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
            <div className="flex items-center gap-2 font-semibold text-[#E3FDFD]">
              <ShieldCheck className="w-4 h-4 text-[#71C9CE]" />
              <span>Positive Defenses</span>
            </div>
            <p className="text-slate-400 text-[11px] font-sans">
              Explicitly verifies and logs every passing defensive control and active shield.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
