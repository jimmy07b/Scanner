import React from "react";
import Link from "next/link";
import { Shield, Lock, Trash2, EyeOff } from "lucide-react";

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-slate-300 font-sans">
      <div className="border-b border-[#1a293e] pb-8 mb-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#71C9CE]/30 bg-[#71C9CE]/10 text-[#CBF1F5] text-xs font-semibold uppercase tracking-wider mb-4 font-mono">
          <Lock className="w-3.5 h-3.5 text-[#71C9CE]" />
          <span>Privacy-First Architecture</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Privacy Policy &amp; Data Handling Principles
        </h1>
        <p className="text-slate-400 text-sm mt-2 font-mono">
          Effective Date: September 2026 • Version 1.0 • RootLayer Trust Framework
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed">
        {/* Core Principles */}
        <section className="rounded-2xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] space-y-4 shadow-xl">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#71C9CE]" />
            <span>Our Core Privacy Commitments</span>
          </h2>
          <p className="text-slate-400">
            RootLayer was engineered under the belief that automated security auditing must never compromise user confidentiality. We maintain the following foundational safeguards:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 font-mono">
            <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
              <strong className="text-[#E3FDFD] text-xs block flex items-center gap-1.5">
                <Trash2 className="w-3.5 h-3.5 text-red-400" /> 24-Hour Automated Purge
              </strong>
              <span className="text-xs text-slate-400 font-sans">
                Uploaded files are automatically overwritten with pseudorandom data and permanently deleted after 24 hours.
              </span>
            </div>

            <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-1">
              <strong className="text-[#E3FDFD] text-xs block flex items-center gap-1.5">
                <EyeOff className="w-3.5 h-3.5 text-[#71C9CE]" /> Zero Code Execution
              </strong>
              <span className="text-xs text-slate-400 font-sans">
                Uploaded documents and archives are never executed or detonated on our systems; analysis is strictly static.
              </span>
            </div>
          </div>
        </section>

        {/* What We Collect */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">1. Information We Collect</h2>
          <p className="text-slate-400">
            When you use our free scanners or submit an audit request, we only collect the minimum telemetry necessary to process your request:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-slate-400">
            <li>
              <strong className="text-[#CBF1F5]">Uploaded Files:</strong> Temporarily stored in an isolated, non-executable directory solely for the duration of the static inspection.
            </li>
            <li>
              <strong className="text-[#CBF1F5]">Website URLs:</strong> Targeted domains submitted for passive HTTP header and TLS inspection.
            </li>
            <li>
              <strong className="text-[#CBF1F5]">Audit Request Data:</strong> Contact name, email address, and organization name when requesting an Advanced Audit.
            </li>
            <li>
              <strong className="text-[#CBF1F5]">Cryptographic Hashes:</strong> SHA-256 and MD5 hashes calculated locally to index findings.
            </li>
          </ul>
        </section>

        {/* How We Process Files */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">2. Static Analysis &amp; Zero-Detonation</h2>
          <p className="text-slate-400">
            All file processing is performed purely through static structural parsing (reading binary headers, PDF tokens, and OOXML relationships). We do not provide dynamic sandbox execution or malware detonation. This ensures that your files cannot compromise our host infrastructure and that no dynamic telemetry is shared with external vendors.
          </p>
        </section>

        {/* File Shredding */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">3. On-Demand &amp; Automated File Shredding</h2>
          <p className="text-slate-400">
            Our retention worker runs continuous purge cycles. Any file that exceeds the retention window is overwritten with zero bytes and deleted from disk. Furthermore, users can click &quot;Purge Upload&quot; directly on their assessment report to instantly trigger permanent disk wiping.
          </p>
        </section>

        {/* Third Party Disclosure */}
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">4. No Data Selling or Commercial Sharing</h2>
          <p className="text-slate-400">
            We do not sell, rent, or trade your uploaded files, contact details, or scan results to any third-party advertisers, data brokers, or threat intelligence platforms.
          </p>
        </section>

        {/* Contact */}
        <section className="pt-6 border-t border-[#1a293e] text-xs text-slate-400 font-mono">
          <p>
            For questions regarding our privacy architecture, contact our team at{" "}
            <a href="mailto:privacy@rootlayer.io" className="text-[#71C9CE] hover:text-[#E3FDFD] underline underline-offset-2">
              privacy@rootlayer.io
            </a>.
          </p>
        </section>
      </div>
    </div>
  );
}
