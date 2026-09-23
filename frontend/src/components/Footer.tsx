import React from "react";
import Link from "next/link";
import { Shield, Lock } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-[#090d16] text-slate-400 text-xs py-10 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          
          {/* Brand Info */}
          <div className="space-y-3">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-6 h-6 rounded-md bg-slate-800 border border-slate-700/80 flex items-center justify-center text-slate-300 group-hover:border-slate-500 transition">
                <Shield className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-white text-sm">RootLayer</span>
            </Link>
            <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
              Security analysis for websites, links, and files.
            </p>
          </div>

          {/* Engine Suite */}
          <div className="space-y-2.5">
            <h4 className="text-slate-300 font-semibold text-xs uppercase tracking-wider font-mono">
              Engine Suite
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li>
                <Link href="/scan/website" className="hover:text-white transition">
                  Website Security Audit
                </Link>
              </li>
              <li>
                <Link href="/scan/url" className="hover:text-white transition">
                  URL Threat Check
                </Link>
              </li>
              <li>
                <Link href="/scan/file" className="hover:text-white transition">
                  Static File Scanner
                </Link>
              </li>
            </ul>
          </div>

          {/* Policy */}
          <div className="space-y-2.5">
            <h4 className="text-slate-300 font-semibold text-xs uppercase tracking-wider font-mono">
              Policy
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li>
                <Link href="/privacy" className="hover:text-white transition">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-white transition">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>

        </div>

        <div className="border-t border-slate-800/80 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <p>© {new Date().getFullYear()} RootLayer. Structured, evidence-based security auditing.</p>
          <span className="font-mono text-[11px] text-slate-500">RootLayer Engine • Passive Recon</span>
        </div>
      </div>
    </footer>
  );
};
