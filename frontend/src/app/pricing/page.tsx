import React from "react";
import Link from "next/link";
import { Check, Shield, ArrowRight, Lock, Radio, Globe, FileSearch } from "lucide-react";

export default function FreeAccessPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Lock className="w-3.5 h-3.5" />
          <span>Our Free &amp; Open Access Commitment</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
          100% Free Cybersecurity Verification
        </h1>
        <p className="text-slate-400 text-base mt-4 leading-relaxed">
          RootLayer was created to give individuals and engineering teams access to reliable, evidence-backed security diagnostics without paywalls, subscriptions, or hidden charges.
        </p>
      </div>

      {/* Free Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
        {/* Engine 1 */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Radio className="w-5 h-5" />
            </div>
            <div className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
              Engine 01 • Free
            </div>
            <h3 className="text-lg font-bold text-white">URL Threat Check</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects brand impersonation, deceptive userinfo (@), numeric IP hostnames, punycode tricks, and multi-hop redirects.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/80">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span>Unlimited Link Checks</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span>Redirect Chain Tracking</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/url"
            className="w-full py-2.5 rounded-lg border border-slate-700 hover:border-cyan-500/50 hover:bg-cyan-950/20 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4"
          >
            <span>Scan URL Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Engine 2 */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Globe className="w-5 h-5" />
            </div>
            <div className="text-xs font-mono font-bold text-teal-400 uppercase tracking-wider">
              Engine 02 • Free
            </div>
            <h3 className="text-lg font-bold text-white">Website Security Audit</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Audits 6 security headers, cookie flags (Secure, HttpOnly, SameSite), robots.txt exposures, and CMS fingerprinting.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/80">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span>CMS &amp; Stack Fingerprinting</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span>Passive Presence Probes</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/website"
            className="w-full py-2.5 rounded-lg border border-slate-700 hover:border-teal-500/50 hover:bg-teal-950/20 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4"
          >
            <span>Audit Website Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Engine 3 */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <FileSearch className="w-5 h-5" />
            </div>
            <div className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
              Engine 03 • Free
            </div>
            <h3 className="text-lg font-bold text-white">Static File Scanner</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Disassembles PDFs, Office docs, images, and archives in memory. Zero execution, 24-hour auto-purge or on-demand shredding.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/80">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Up to 50MB per file</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Automated 24h File Shredding</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/file"
            className="w-full py-2.5 rounded-lg border border-slate-700 hover:border-emerald-500/50 hover:bg-emerald-950/20 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4"
          >
            <span>Scan File Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Principles Section */}
      <div className="max-w-4xl mx-auto glass-panel rounded-2xl p-8 border border-slate-800 space-y-6">
        <h3 className="text-xl font-bold text-white">Our 3 Core Principles</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs text-slate-300">
          <div className="space-y-2">
            <span className="font-bold text-cyan-400 block text-sm">1. No Check, No Finding</span>
            <p className="text-slate-400 leading-relaxed">
              We never invent low-risk issues to fill empty pages. If evidence is missing, no finding is generated.
            </p>
          </div>
          <div className="space-y-2">
            <span className="font-bold text-teal-400 block text-sm">2. Zero Execution</span>
            <p className="text-slate-400 leading-relaxed">
              Binary files are analyzed purely through memory-safe structural parsing. Code is never executed.
            </p>
          </div>
          <div className="space-y-2">
            <span className="font-bold text-emerald-400 block text-sm">3. Privacy-First</span>
            <p className="text-slate-400 leading-relaxed">
              No tracking cookies, no telemetry sales, and automated scheduled file deletion within 24 hours.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
