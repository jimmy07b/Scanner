"use client";

import React, { useState } from "react";
import { Finding } from "@/lib/api";
import { RiskBadge } from "./RiskBadge";
import { CheckCircle2, Copy, Check, ChevronDown, ChevronUp, Terminal, ShieldAlert } from "lucide-react";

interface FindingsListProps {
  findings: Finding[];
}

export const FindingsList: React.FC<FindingsListProps> = ({ findings }) => {
  const [filter, setFilter] = useState<string>("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const filterOptions = [
    { label: "All Findings", value: "all", count: findings.length },
    { label: "Critical", value: "critical", count: findings.filter((f) => f.severity.toLowerCase() === "critical").length },
    { label: "High", value: "high", count: findings.filter((f) => f.severity.toLowerCase() === "high").length },
    { label: "Medium", value: "medium", count: findings.filter((f) => f.severity.toLowerCase() === "medium").length },
    { label: "Low", value: "low", count: findings.filter((f) => f.severity.toLowerCase() === "low").length },
    { label: "Info", value: "info", count: findings.filter((f) => f.severity.toLowerCase() === "info").length },
  ];

  const filtered = findings.filter((f) => {
    if (filter === "all") return true;
    return f.severity.toLowerCase() === filter;
  });

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleExpand = (index: number) => {
    setExpandedId(expandedId === index ? null : index);
  };

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 pb-2 border-b border-slate-800">
        {filterOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setFilter(opt.value)}
            disabled={opt.count === 0 && opt.value !== "all"}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              filter === opt.value
                ? "bg-[#131e2e] text-[#E3FDFD] border border-[#71C9CE] font-semibold shadow-sm"
                : opt.count === 0
                ? "bg-[#0d1522]/40 text-slate-600 cursor-not-allowed border border-[#1a293e]/40"
                : "bg-[#0d1522] text-slate-400 hover:text-[#CBF1F5] border border-[#1a293e] hover:border-[#324b6d]"
            }`}
          >
            {opt.label}
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${filter === opt.value ? "bg-[#71C9CE]/20 text-[#CBF1F5]" : "bg-[#070b12] text-slate-400"}`}>
              {opt.count}
            </span>
          </button>
        ))}
      </div>

      {/* Findings Content */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 rounded-xl border border-dashed border-slate-800 bg-slate-950/40">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
          <h4 className="text-slate-200 font-semibold text-base">No Security Issues Found</h4>
          <p className="text-slate-400 text-sm max-w-md mx-auto mt-1">
            {filter === "all"
              ? "All static security checks passed cleanly with no suspicious patterns or headers missing."
              : `No findings matching the '${filter.toUpperCase()}' severity filter.`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item, idx) => {
            const isExpanded = expandedId === idx || filtered.length <= 3;
            return (
              <div
                key={idx}
                className="rounded-xl border border-slate-800 bg-slate-900/70 overflow-hidden transition-all hover:border-slate-700"
              >
                {/* Header */}
                <div
                  onClick={() => toggleExpand(idx)}
                  className="p-4 flex items-start justify-between cursor-pointer select-none gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 flex-wrap">
                      <RiskBadge status={item.severity} size="sm" />
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {item.category}
                      </span>
                      {item.finding_key && (
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-950 text-cyan-400 border border-slate-800">
                          {item.finding_key}
                        </span>
                      )}
                      {item.confidence && (
                        <span
                          className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${
                            item.confidence.toLowerCase() === "high"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : item.confidence.toLowerCase() === "medium"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {item.confidence} confidence
                        </span>
                      )}
                    </div>
                    <h4 className="text-slate-100 font-semibold text-sm sm:text-base">
                      {item.title}
                    </h4>
                  </div>
                  <button className="text-slate-400 hover:text-slate-200 mt-1">
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>
                </div>

                {/* Body Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-800/60 text-sm">
                    {/* Evidence */}
                    {item.evidence && (
                      <div>
                        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                          <Terminal className="w-3.5 h-3.5 text-slate-400" /> Evidence / Detected Values
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-950 font-mono text-xs text-slate-300 border border-slate-800/80 break-all whitespace-pre-wrap">
                          {Array.isArray(item.evidence) ? (item.evidence as string[]).join("\n") : item.evidence}
                        </div>
                      </div>
                    )}

                    {/* Recommendation */}
                    {item.recommendation && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                            <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" /> Recommended Action & Fix
                          </div>
                          <button
                            onClick={() => handleCopy(item.recommendation || "", idx)}
                            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 py-0.5 px-2 rounded hover:bg-slate-800 transition"
                          >
                            {copiedIndex === idx ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-400" /> Copied
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" /> Copy Fix
                              </>
                            )}
                          </button>
                        </div>
                        <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-slate-200 text-xs sm:text-sm font-mono whitespace-pre-wrap">
                          {item.recommendation}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
