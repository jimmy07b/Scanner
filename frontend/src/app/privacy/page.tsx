import React from "react";
import Link from "next/link";
import { Shield, Lock, Trash2, EyeOff, CheckCircle } from "lucide-react";

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-slate-300">
      <div className="border-b border-slate-800 pb-8 mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Lock className="w-3.5 h-3.5" />
          <span>Privacy-First Architecture</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Privacy Policy &amp; Data Handling Principles
        </h1>
        <p className="text-slate-400 text-sm mt-2">
          Effective Date: September 2026 • Version 1.0
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed">
        {/* Core Principles */}
        <section className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            Our Core Privacy Commitments
          </h2>
          <p>
            RootLayer was engineered from the ground up under the belief that security auditing should never come at the expense of user confidentiality. We maintain the following foundational safeguards:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <strong className="text-white text-xs block flex items-center gap-1.5">
                <Trash2 className="w-3.5 h-3.5 text-red-400" /> 24-Hour Automated Purge
              </strong>
              <span className="text-xs text-slate-400">
                Uploaded files are automatically shredded and overwritten after 24 hours.
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <strong className="text-white text-xs block flex items-center gap-1.5">
                <EyeOff className="w-3.5 h-3.5 text-emerald-400" /> Zero Code Execution
              </strong>
              <span className="text-xs text-slate-400">
                Uploaded documents and binaries are never run, executed, or detonated on our systems.
              </span>
            </div>
          </div>
        </section>

        {/* What We Collect */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">1. Information We Collect</h2>
          <p>
            When you use our free scanners or submit an audit request, we only collect the minimum telemetry necessary to process your request:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>
              <strong className="text-slate-200">Uploaded Files:</strong> Temporarily stored in an isolated, non-executable directory solely for the duration of the static inspection.
            </li>
            <li>
              <strong className="text-slate-200">Website URLs:</strong> Targeted domains submitted for passive HTTP header and TLS inspection.
            </li>
            <li>
              <strong className="text-slate-200">Audit Request Data:</strong> Contact name, email address, and organization name when requesting an Advanced Audit (₹1,999).
            </li>
            <li>
              <strong className="text-slate-200">Cryptographic Hashes:</strong> SHA-256, MD5, and SHA-1 hashes calculated locally to index findings.
            </li>
          </ul>
        </section>

        {/* How We Process Files */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">2. Static Analysis &amp; Zero-Detonation</h2>
          <p>
            All file processing is performed purely through static structural parsing (reading binary headers, PDF tokens, and OOXML XML relationships). We do not provide dynamic sandbox execution or malware detonation. This ensures that your files cannot compromise our host infrastructure and that no dynamic telemetry is shared with external vendors.
          </p>
        </section>

        {/* File Shredding */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">3. On-Demand &amp; Automated File Shredding</h2>
          <p>
            Our retention worker runs continuous purge cycles. Any file that exceeds the 24-hour retention window is overwritten with zero bytes and deleted from disk. Furthermore, users can click the &quot;Shred File Now&quot; button directly on their assessment report to instantly trigger permanent disk wiping.
          </p>
        </section>

        {/* Third Party Disclosure */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">4. No Data Selling or Commercial Sharing</h2>
          <p>
            We do not sell, rent, or trade your uploaded files, contact details, or scan results to any third-party advertisers, data brokers, or threat intelligence platforms.
          </p>
        </section>

        {/* Contact */}
        <section className="pt-6 border-t border-slate-800 text-xs text-slate-400">
          <p>
            For questions regarding our privacy architecture or to request manual deletion of your contact records, contact our Data Protection Officer at{" "}
            <a href="mailto:privacy@rootlayer.io" className="text-cyan-400 hover:underline">
              privacy@rootlayer.io
            </a>.
          </p>
        </section>
      </div>
    </div>
  );
}
