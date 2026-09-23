import React from "react";
import Link from "next/link";
import { ShieldAlert, AlertOctagon } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-slate-300 font-sans">
      <div className="border-b border-[#1a293e] pb-8 mb-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <ShieldAlert className="w-3.5 h-3.5 text-[#71C9CE]" />
          <span>Acceptable Use &amp; Terms</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Terms of Service &amp; Acceptable Use
        </h1>
        <p className="text-slate-400 text-sm mt-2 font-mono">
          Effective Date: September 2026 • Version 1.0 • RootLayer Trust Framework
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed">
        {/* Strict Authorization Requirement */}
        <section className="p-6 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-3">
          <h2 className="text-base font-bold text-amber-400 flex items-center gap-2 font-mono">
            <AlertOctagon className="w-5 h-5 text-amber-400" />
            Mandatory Authorization Requirement
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
            You must ONLY scan files or audit websites that you own, or for which you have received express, documented authorization from the owner. Scanning third-party web assets without consent may violate applicable computer misuse laws, including India&apos;s Information Technology Act, the US Computer Fraud and Abuse Act (CFAA), and equivalent international legislation.
          </p>
        </section>

        {/* Permitted Uses */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">1. Permitted Use Cases</h2>
          <p className="text-slate-400">RootLayer is designed exclusively for defensive, educational, and audit hygiene purposes, including:</p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>Checking documents, PDFs, or archives received via email for macro risks or embedded scripts.</li>
            <li>Auditing your own company web application for missing HTTP security headers (CSP, HSTS, X-Frame-Options).</li>
            <li>Evaluating cookie security flags and SSL/TLS configuration best practices.</li>
            <li>Checking suspicious links for brand impersonation and executable payloads.</li>
          </ul>
        </section>

        {/* Prohibited Uses */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">2. Strictly Prohibited Activities</h2>
          <p className="text-slate-400">You agree not to use the RootLayer platform for:</p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>Attempting denial-of-service (DoS/DDoS) attacks or bombarding target websites with excessive requests.</li>
            <li>Uploading zero-day exploit payloads or weapons with intent to distribute.</li>
            <li>Automating high-frequency reconnaissance against unauthorized third-party infrastructure.</li>
            <li>Attempting to bypass our rate limiters or reverse engineer proprietary scanners.</li>
          </ul>
        </section>

        {/* Disclaimers & Warranties */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">3. Disclaimer of Warranties</h2>
          <p className="text-slate-400 leading-relaxed">
            RootLayer performs non-destructive passive reconnaissance, header inspection, and heuristic checks. While our engines detect a wide spectrum of known risks, static analysis cannot guarantee the total absence of security vulnerabilities or zero-day threats. The platform and its assessment reports are provided &quot;AS IS&quot; without warranties of any kind.
          </p>
        </section>

        <section className="pt-6 border-t border-[#1a293e] text-xs text-slate-400 font-mono">
          <p>
            If you have questions regarding these terms, please contact legal counsel at{" "}
            <a href="mailto:legal@rootlayer.io" className="text-[#71C9CE] hover:text-[#E3FDFD] underline underline-offset-2">
              legal@rootlayer.io
            </a>.
          </p>
        </section>
      </div>
    </div>
  );
}
