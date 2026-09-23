import React from "react";
import {
  ShieldCheck,
  AlertTriangle,
  ShieldAlert,
  AlertOctagon,
  Info,
  Clock,
  RefreshCw,
  XCircle,
  HelpCircle,
  Radio,
  FileWarning,
} from "lucide-react";

interface RiskBadgeProps {
  status:
    | "clean"
    | "safe"
    | "low"
    | "medium"
    | "high"
    | "critical"
    | "suspicious"
    | "phishing-like"
    | "redirect-heavy"
    | "malware-linked"
    | "unreachable"
    | "queued"
    | "running"
    | "completed"
    | "failed"
    | string;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  status,
  size = "md",
  showIcon = true,
}) => {
  const normalized = (status || "").toLowerCase().replace(/_/g, "-");

  const config: Record<
    string,
    { label: string; bg: string; icon: React.ComponentType<{ className?: string }> }
  > = {
    clean: {
      label: "Compliant / Clean",
      bg: "bg-emerald-950/30 text-emerald-400 border-emerald-800/50",
      icon: ShieldCheck,
    },
    safe: {
      label: "Safe / Passed",
      bg: "bg-emerald-950/30 text-emerald-400 border-emerald-800/50",
      icon: ShieldCheck,
    },
    low: {
      label: "Low Risk",
      bg: "bg-slate-800/80 text-slate-300 border-slate-700/80",
      icon: Info,
    },
    medium: {
      label: "Medium Risk",
      bg: "bg-amber-950/40 text-amber-400 border-amber-800/60",
      icon: AlertTriangle,
    },
    high: {
      label: "High Risk",
      bg: "bg-orange-950/40 text-orange-400 border-orange-800/60",
      icon: ShieldAlert,
    },
    critical: {
      label: "Critical Severity",
      bg: "bg-red-950/50 text-red-400 border-red-800/70",
      icon: AlertOctagon,
    },
    suspicious: {
      label: "Suspicious",
      bg: "bg-amber-950/40 text-amber-400 border-amber-800/60",
      icon: AlertTriangle,
    },
    "phishing-like": {
      label: "Phishing Indicator",
      bg: "bg-red-950/50 text-red-400 border-red-800/70",
      icon: AlertOctagon,
    },
    "redirect-heavy": {
      label: "Multiple Hops",
      bg: "bg-slate-800/80 text-slate-300 border-slate-700/80",
      icon: Radio,
    },
    "malware-linked": {
      label: "Malware Associated",
      bg: "bg-red-950/50 text-red-400 border-red-800/70",
      icon: FileWarning,
    },
    unreachable: {
      label: "Host Unreachable",
      bg: "bg-zinc-800 text-zinc-400 border-zinc-700",
      icon: XCircle,
    },
    queued: {
      label: "Queued",
      bg: "bg-zinc-800 text-zinc-400 border-zinc-700",
      icon: Clock,
    },
    running: {
      label: "In Progress",
      bg: "bg-zinc-800 text-zinc-300 border-zinc-700",
      icon: RefreshCw,
    },
    completed: {
      label: "Finalized",
      bg: "bg-emerald-950/30 text-emerald-400 border-emerald-800/50",
      icon: ShieldCheck,
    },
    failed: {
      label: "Execution Failed",
      bg: "bg-red-950/50 text-red-400 border-red-800/70",
      icon: XCircle,
    },
    info: {
      label: "Informational",
      bg: "bg-zinc-800/80 text-zinc-400 border-zinc-700",
      icon: Info,
    },
  };

  const matched = config[normalized] || {
    label: (status || "UNKNOWN").toUpperCase(),
    bg: "bg-zinc-800 text-zinc-400 border-zinc-700",
    icon: HelpCircle,
  };

  const IconComponent = matched.icon;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-[11px]",
    lg: "px-3 py-1.5 text-xs",
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-semibold rounded border ${matched.bg} ${sizeClasses} uppercase tracking-wider`}
    >
      {showIcon && <IconComponent className={size === "lg" ? "w-3.5 h-3.5 shrink-0" : "w-3 h-3 shrink-0"} />}
      <span>{matched.label}</span>
    </span>
  );
};
