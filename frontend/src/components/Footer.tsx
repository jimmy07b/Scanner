import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#1a293e] bg-[#070b12] text-slate-400 text-xs py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          
          {/* Brand Info */}
          <div className="space-y-3">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-7 h-7 rounded-lg bg-[#0d1522] border border-[#71C9CE]/40 flex items-center justify-center text-[#71C9CE] group-hover:border-[#71C9CE] group-hover:shadow-sm group-hover:shadow-[#71C9CE]/20 transition">
                <Shield className="w-4 h-4 text-[#71C9CE]" />
              </div>
              <span className="font-bold text-[#E3FDFD] text-base group-hover:text-white transition">
                RootLayer
              </span>
            </Link>
            <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
              Precision automated cybersecurity intelligence and evidence-based posture analysis for websites, URLs, and files.
            </p>
          </div>

          {/* Engine Suite */}
          <div className="space-y-2.5">
            <h4 className="text-[#CBF1F5] font-semibold text-xs uppercase tracking-wider font-mono">
              Security Engines
            </h4>
            <ul className="space-y-2 text-xs text-slate-400 font-medium">
              <li>
                <Link href="/scan/website" className="hover:text-[#E3FDFD] transition flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#71C9CE]" />
                  <span>Website Security Audit</span>
                </Link>
              </li>
              <li>
                <Link href="/scan/url" className="hover:text-[#E3FDFD] transition flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#A6E3E9]" />
                  <span>URL Threat Check</span>
                </Link>
              </li>
              <li>
                <Link href="/scan/file" className="hover:text-[#E3FDFD] transition flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#CBF1F5]" />
                  <span>Static File Scanner</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Policy & Governance */}
          <div className="space-y-2.5">
            <h4 className="text-[#CBF1F5] font-semibold text-xs uppercase tracking-wider font-mono">
              Policy &amp; Standards
            </h4>
            <ul className="space-y-2 text-xs text-slate-400 font-medium">
              <li>
                <Link href="/privacy" className="hover:text-[#E3FDFD] transition">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-[#E3FDFD] transition">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="hover:text-[#E3FDFD] transition">
                  Open Access Standard
                </Link>
              </li>
            </ul>
          </div>

        </div>

        <div className="border-t border-[#1a293e] mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3 font-mono">
          <p className="text-slate-400">
            © {new Date().getFullYear()} RootLayer Security. Non-destructive telemetry &amp; ASVS compliance.
          </p>
          <span className="text-[#71C9CE] text-[11px]">
            RootLayer Reconnaissance Platform • Evidence First
          </span>
        </div>
      </div>
    </footer>
  );
};
