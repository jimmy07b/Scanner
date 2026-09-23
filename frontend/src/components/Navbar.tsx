"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Shield, FileSearch, Globe, Menu, X, Radio } from "lucide-react";

export const Navbar: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#0b101b]/95 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center text-slate-200 group-hover:border-slate-500 transition">
              <Shield className="w-4 h-4 text-slate-300" />
            </div>
            <span className="font-bold text-base tracking-tight text-white">
              RootLayer
            </span>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-4 text-xs font-medium text-slate-400">
            <Link
              href="/scan/website"
              className="text-slate-200 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Globe className="w-3.5 h-3.5 text-slate-400" />
              <span>Website Audit</span>
            </Link>
            <span className="text-slate-700">·</span>
            <Link
              href="/scan/url"
              className="hover:text-slate-200 transition-colors flex items-center gap-1.5"
            >
              <Radio className="w-3.5 h-3.5 text-slate-400" />
              <span>URL Check</span>
            </Link>
            <span className="text-slate-700">·</span>
            <Link
              href="/scan/file"
              className="hover:text-slate-200 transition-colors flex items-center gap-1.5"
            >
              <FileSearch className="w-3.5 h-3.5 text-slate-400" />
              <span>File Scanner</span>
            </Link>
          </div>

          {/* Mobile hamburger */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-b border-slate-800 bg-[#0b101b] px-4 pt-2 pb-5 space-y-2">
          <Link
            href="/scan/website"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-2 text-slate-200 py-2 hover:text-white text-sm font-medium"
          >
            <Globe className="w-4 h-4 text-slate-400" /> Website Audit
          </Link>
          <Link
            href="/scan/url"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-2 text-slate-400 py-2 hover:text-slate-200 text-sm"
          >
            <Radio className="w-4 h-4" /> URL Check
          </Link>
          <Link
            href="/scan/file"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-2 text-slate-400 py-2 hover:text-slate-200 text-sm"
          >
            <FileSearch className="w-4 h-4" /> File Scanner
          </Link>
        </div>
      )}
    </nav>
  );
};
