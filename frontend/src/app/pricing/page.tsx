import React from "react";
import Link from "next/link";
import { Check, ArrowRight, Lock, Radio, Globe, FileSearch } from "lucide-react";

export default function FreeAccessPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 font-sans">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <Lock className="w-3.5 h-3.5 text-[#71C9CE]" />
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
        <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] space-y-4 flex flex-col justify-between shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#71C9CE]/15 border border-[#71C9CE]/30 flex items-center justify-center text-[#71C9CE]">
              <Radio className="w-5 h-5 text-[#71C9CE]" />
            </div>
            <div className="text-xs font-mono font-bold text-[#71C9CE] uppercase tracking-wider">
              Engine 01 • Core Free
            </div>
            <h3 className="text-lg font-bold text-white">URL Threat Check</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Detects brand impersonation, deceptive userinfo (@), numeric IP hostnames, punycode tricks, and multi-hop redirects.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-[#1a293e] font-sans">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#71C9CE] shrink-0" />
                <span>Unlimited Link Checks</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#71C9CE] shrink-0" />
                <span>Redirect Chain Tracking</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/url"
            className="w-full py-2.5 rounded-lg border border-[#1a293e] bg-[#070b12] hover:border-[#71C9CE] text-[#CBF1F5] hover:text-[#E3FDFD] text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4 font-mono"
          >
            <span>Scan URL Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Engine 2 */}
        <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] space-y-4 flex flex-col justify-between shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#A6E3E9]/15 border border-[#A6E3E9]/30 flex items-center justify-center text-[#A6E3E9]">
              <Globe className="w-5 h-5 text-[#A6E3E9]" />
            </div>
            <div className="text-xs font-mono font-bold text-[#A6E3E9] uppercase tracking-wider">
              Engine 02 • Core Free
            </div>
            <h3 className="text-lg font-bold text-white">Website Security Audit</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Audits 6 security headers, cookie flags (Secure, HttpOnly, SameSite), robots.txt exposures, and CMS fingerprinting.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-[#1a293e] font-sans">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#A6E3E9] shrink-0" />
                <span>CMS &amp; Stack Fingerprinting</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#A6E3E9] shrink-0" />
                <span>Passive Presence Probes</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/website"
            className="w-full py-2.5 rounded-lg border border-[#1a293e] bg-[#070b12] hover:border-[#A6E3E9] text-[#CBF1F5] hover:text-[#E3FDFD] text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4 font-mono"
          >
            <span>Audit Website Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Engine 3 */}
        <div className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] space-y-4 flex flex-col justify-between shadow-xl">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#CBF1F5]/15 border border-[#CBF1F5]/30 flex items-center justify-center text-[#CBF1F5]">
              <FileSearch className="w-5 h-5 text-[#CBF1F5]" />
            </div>
            <div className="text-xs font-mono font-bold text-[#CBF1F5] uppercase tracking-wider">
              Engine 03 • Core Free
            </div>
            <h3 className="text-lg font-bold text-white">Static File Scanner</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Disassembles PDFs, Office docs, images, and archives in memory. Zero execution, 24-hour auto-purge or on-demand shredding.
            </p>
            <ul className="space-y-2 text-xs text-slate-300 pt-2 border-t border-[#1a293e] font-sans">
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#CBF1F5] shrink-0" />
                <span>Up to 50MB per file</span>
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-3.5 h-3.5 text-[#CBF1F5] shrink-0" />
                <span>Automated 24h File Shredding</span>
              </li>
            </ul>
          </div>
          <Link
            href="/scan/file"
            className="w-full py-2.5 rounded-lg border border-[#1a293e] bg-[#070b12] hover:border-[#CBF1F5] text-[#CBF1F5] hover:text-[#E3FDFD] text-xs font-semibold flex items-center justify-center gap-1.5 transition mt-4 font-mono"
          >
            <span>Scan File Now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Principles Section */}
      <div className="max-w-4xl mx-auto rounded-2xl p-8 border border-[#1a293e] bg-[#0d1522] space-y-6 shadow-xl">
        <h3 className="text-xl font-bold text-white font-sans">Our 3 Core Principles</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs text-slate-300 font-sans">
          <div className="space-y-2">
            <span className="font-bold text-[#71C9CE] block text-sm font-mono">1. No Check, No Finding</span>
            <p className="text-slate-400 leading-relaxed">
              We never invent low-risk issues to fill empty pages. If evidence is missing, zero synthetic findings are generated.
            </p>
          </div>
          <div className="space-y-2">
            <span className="font-bold text-[#A6E3E9] block text-sm font-mono">2. Zero Execution</span>
            <p className="text-slate-400 leading-relaxed">
              Binary files are analyzed purely through memory-safe structural parsing. Code is never executed.
            </p>
          </div>
          <div className="space-y-2">
            <span className="font-bold text-[#CBF1F5] block text-sm font-mono">3. Privacy-First</span>
            <p className="text-slate-400 leading-relaxed">
              No tracking cookies, no telemetry sales, and automated scheduled file deletion within 24 hours.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
