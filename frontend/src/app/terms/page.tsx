import React from "react";
import Link from "next/link";
import { ShieldAlert, CheckCircle2, AlertOctagon } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-slate-300">
      <div className="border-b border-slate-800 pb-8 mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Acceptable Use &amp; Terms</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Terms of Service &amp; Acceptable Use
        </h1>
        <p className="text-slate-400 text-sm mt-2">
          Effective Date: September 2026 • Version 1.0
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed">
        {/* Strict Authorization Requirement */}
        <section className="p-6 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-3">
          <h2 className="text-base font-bold text-amber-400 flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-amber-400" />
            Mandatory Authorization Requirement
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            You must ONLY scan files or audit websites that you own, or for which you have received express, documented authorization from the owner. Scanning third-party web assets without consent may violate applicable computer misuse laws, including India&apos;s Information Technology Act, the US Computer Fraud and Abuse Act (CFAA), and equivalent international legislation.
          </p>
        </section>

        {/* Permitted Uses */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">1. Permitted Use Cases</h2>
          <p>RootLayer is designed exclusively for defensive, educational, and audit hygiene purposes, including:</p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>Checking documents, PDFs, or archives received via email for macro risks or embedded scripts.</li>
            <li>Auditing your own company web application for missing HTTP security headers (CSP, HSTS, X-Frame-Options).</li>
            <li>Evaluating cookie security flags and SSL/TLS configuration best practices.</li>
            <li>Booking in-depth manual security reviews with our certified engineering team.</li>
          </ul>
        </section>

        {/* Prohibited Uses */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">2. Strictly Prohibited Activities</h2>
          <p>You agree not to use the RootLayer platform for:</p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>Attempting denial-of-service (DoS/DDoS) attacks or bombarding target websites with excessive requests.</li>
            <li>Uploading zero-day exploit payloads or weapons with intent to distribute.</li>
            <li>Automating high-frequency reconnaissance against unauthorized third-party infrastructure.</li>
            <li>Attempting to bypass our rate limiters, reverse engineer our proprietary scanners, or compromise server security.</li>
          </ul>
        </section>

        {/* Disclaimers & Warranties */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">3. Disclaimer of Warranties</h2>
          <p className="text-slate-400">
            RootLayer performs static pattern matching, header inspection, and heuristic checks. While our engines detect a wide spectrum of known risks, static analysis cannot guarantee the total absence of security vulnerabilities or zero-day threats. The platform and its assessment reports are provided &quot;AS IS&quot; without warranties of any kind.
          </p>
        </section>

        {/* Advanced Audit Engagement Terms */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">4. Advanced Website Security Audit (₹1,999)</h2>
          <p className="text-slate-400">
            When ordering an Advanced Website Security Audit:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>Audits are conducted within our standard SLA window of 24–48 business hours following confirmed payment.</li>
            <li>The assessment includes one complimentary re-test within 30 days of deliverable issuance.</li>
            <li>All technical findings and reports are treated as strictly confidential client material.</li>
          </ul>
        </section>

        <section className="pt-6 border-t border-slate-800 text-xs text-slate-400">
          <p>
            If you have questions regarding these terms, please contact legal counsel at{" "}
            <a href="mailto:legal@rootlayer.io" className="text-cyan-400 hover:underline">
              legal@rootlayer.io
            </a>.
          </p>
        </section>
      </div>
    </div>
  );
}
