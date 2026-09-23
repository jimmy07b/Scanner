"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Lock,
  ShieldAlert,
  FileCheck,
  Trash2,
  CheckCircle,
  AlertTriangle,
  LogOut,
  RefreshCw,
  ExternalLink,
  MessageSquare,
  Clock,
  Send,
  Globe,
  Radio,
  FileSearch,
  Server
} from "lucide-react";
import { api, AdminMetrics, AuditRequest } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import { formatDate } from "@/lib/utils";

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);

  // Login states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  // Dashboard states: default to real live scans feed
  const [activeTab, setActiveTab] = useState<"scans" | "retention" | "audits">("scans");
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [audits, setAudits] = useState<AuditRequest[]>([]);
  const [scans, setScans] = useState<any[]>([]);
  const [dataLoading, setDataLoading] = useState(false);

  // Internal Notes modal states
  const [activeNoteTarget, setActiveNoteTarget] = useState<string | null>(null);
  const [notesList, setNotesList] = useState<any[]>([]);
  const [newNoteText, setNewNoteText] = useState("");
  const [noteLoading, setNoteLoading] = useState(false);

  // Retention Purge state
  const [purging, setPurging] = useState(false);
  const [purgeFeedback, setPurgeFeedback] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("rootlayer_admin_token") || localStorage.getItem("aegis_admin_token");
    if (saved) {
      setToken(saved);
    }
  }, []);

  useEffect(() => {
    if (token) {
      loadDashboardData();
    }
  }, [token]);

  const loadDashboardData = async () => {
    if (!token) return;
    setDataLoading(true);
    try {
      const [m, a, s] = await Promise.all([
        api.getAdminMetrics(token),
        api.getAdminAudits(token),
        api.getAdminScans(token),
      ]);
      setMetrics(m);
      setAudits(a);
      setScans(s);
    } catch (err: any) {
      if (err.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setDataLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError("");

    try {
      const res = await api.adminLogin(email.trim(), password);
      localStorage.setItem("rootlayer_admin_token", res.access_token);
      setToken(res.access_token);
    } catch (err: any) {
      setLoginError(err.response?.data?.detail || "Invalid admin credentials");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("rootlayer_admin_token");
    localStorage.removeItem("aegis_admin_token");
    setToken(null);
  };

  const handleUpdateAuditStatus = async (auditId: string, newStatus: string) => {
    if (!token) return;
    try {
      const updated = await api.updateAuditStatus(auditId, { status: newStatus }, token);
      setAudits(audits.map((a) => (a.id === auditId ? updated : a)));
    } catch (err: any) {
      alert("Failed to update status: " + (err.response?.data?.detail || err.message));
    }
  };

  const openNotesModal = async (auditId: string) => {
    if (!token) return;
    setActiveNoteTarget(auditId);
    setNoteLoading(true);
    try {
      const notes = await api.getAdminNotes("audit", auditId, token);
      setNotesList(notes);
    } catch (err) {
      setNotesList([]);
    } finally {
      setNoteLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !activeNoteTarget || !newNoteText.trim()) return;

    try {
      const note = await api.createAdminNote(
        { target_type: "audit", target_id: activeNoteTarget, note: newNoteText.trim() },
        token
      );
      setNotesList([note, ...notesList]);
      setNewNoteText("");
    } catch (err: any) {
      alert("Failed to add note: " + (err.response?.data?.detail || err.message));
    }
  };

  const handlePurge = async () => {
    if (!token) return;
    setPurging(true);
    setPurgeFeedback(null);
    try {
      const res = await api.purgeExpiredFiles(token);
      setPurgeFeedback(`Purge complete: ${res.stats?.shredded_successfully || 0} expired files shredded.`);
      loadDashboardData();
    } catch (err: any) {
      alert("Purge failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setPurging(false);
    }
  };

  // 1. Unauthenticated Login Screen
  if (!token) {
    return (
      <div className="max-w-md mx-auto px-4 py-24">
        <div className="rounded-2xl p-8 border border-slate-800 bg-[#0c121e] shadow-2xl">
          <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200 mx-auto mb-4">
            <Lock className="w-5 h-5" />
          </div>
          <h2 className="text-xl font-bold text-white text-center">RootLayer Administration</h2>
          <p className="text-xs text-slate-400 text-center mt-1">
            Sign in to inspect system telemetry, live scans, and retention storage.
          </p>

          <form onSubmit={handleLogin} className="mt-8 space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Admin Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@rootlayer.io"
                className="w-full px-4 py-2.5 rounded-lg bg-[#090d16] border border-slate-800 text-white text-sm focus:outline-none focus:border-slate-600"
                required
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-[#090d16] border border-slate-800 text-white text-sm focus:outline-none focus:border-slate-600"
                required
              />
            </div>

            {loginError && (
              <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-400 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loginLoading}
              className="w-full py-2.5 rounded-lg bg-slate-100 hover:bg-white text-slate-900 font-semibold text-sm transition disabled:opacity-50 mt-2"
            >
              {loginLoading ? "Authenticating..." : "Sign In to Operations"}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-500 text-center">
            Protected Administrative Gateway • Authorized Personnel Only
          </div>
        </div>
      </div>
    );
  }

  // 2. Authenticated Admin Dashboard
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 mb-8 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Platform Telemetry
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            RootLayer Administration
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadDashboardData}
            disabled={dataLoading}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${dataLoading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-800 text-slate-400 hover:text-red-400 hover:border-red-500/30 text-xs font-semibold transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Operational KPI Cards */}
      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="rounded-xl p-5 border border-slate-800 bg-[#0c121e] space-y-1">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Total Security Scans</div>
            <div className="text-2xl font-extrabold text-white font-mono">{metrics.total_scans}</div>
            <div className="text-[11px] text-slate-500">
              {metrics.total_website_scans || 0} Websites • {metrics.total_url_scans} URLs • {metrics.total_file_scans} Files
            </div>
          </div>

          <div className="rounded-xl p-5 border border-slate-800 bg-[#0c121e] space-y-1">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Threats &amp; High Risk</div>
            <div className="text-2xl font-extrabold text-red-400 font-mono">
              {metrics.threats_flagged}
            </div>
            <div className="text-[11px] text-slate-500">High / Critical risk detections</div>
          </div>

          <div className="rounded-xl p-5 border border-slate-800 bg-[#0c121e] space-y-1">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Retained File Storage</div>
            <div className="text-2xl font-extrabold text-slate-100 font-mono">
              {metrics.active_files_stored}
            </div>
            <div className="text-[11px] text-slate-500">Uploads under 24h retention policy</div>
          </div>

          <div className="rounded-xl p-5 border border-slate-800 bg-[#0c121e] space-y-1">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Detection Engine Suite</div>
            <div className="text-2xl font-extrabold text-emerald-400 font-mono">
              3 / 3 Active
            </div>
            <div className="text-[11px] text-slate-500">Website, URL Threat, Static File engines</div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 mb-6 gap-6 text-xs sm:text-sm font-semibold">
        <button
          onClick={() => setActiveTab("scans")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "scans"
              ? "border-slate-100 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Live Scan Feed ({scans.length})
        </button>
        <button
          onClick={() => setActiveTab("retention")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "retention"
              ? "border-slate-100 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          File Retention &amp; Storage
        </button>
        <button
          onClick={() => setActiveTab("audits")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "audits"
              ? "border-slate-100 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Audit Requests ({audits.length})
        </button>
      </div>

      {/* TAB 1: Live Scan Feed */}
      {activeTab === "scans" && (
        <div className="rounded-xl border border-slate-800 bg-[#0c121e] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#090d16] text-slate-400 uppercase text-[10px] font-mono border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Engine</th>
                  <th className="px-4 py-3.5">Target</th>
                  <th className="px-4 py-3.5">Risk Score</th>
                  <th className="px-4 py-3.5">Verdict</th>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5 text-right">Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {scans.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-slate-500">
                      No security scans recorded yet.
                    </td>
                  </tr>
                ) : (
                  scans.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-900/40">
                      <td className="px-4 py-3.5">
                        <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase">
                          {s.scan_type}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-mono font-medium text-white max-w-xs truncate" title={s.target_name}>
                        {s.target_name}
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-slate-200">{s.risk_score} / 100</td>
                      <td className="px-4 py-3.5">
                        <RiskBadge status={s.status} size="sm" />
                      </td>
                      <td className="px-4 py-3.5 text-slate-400">{formatDate(s.created_at)}</td>
                      <td className="px-4 py-3.5 text-right">
                        <Link
                          href={`/reports/${s.id}`}
                          className="text-slate-300 hover:text-white inline-flex items-center gap-1 font-medium transition"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="w-3 h-3 text-slate-500" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: Retention & Storage */}
      {activeTab === "retention" && (
        <div className="rounded-xl p-6 sm:p-8 border border-slate-800 bg-[#0c121e] space-y-6 max-w-3xl">
          <div>
            <h3 className="text-base font-bold text-white">Storage Lifecycle &amp; Retention Policy</h3>
            <p className="text-xs text-slate-400 mt-1">
              RootLayer statically inspects files and enforces an automated retention policy to eliminate indefinite storage of uploaded payloads.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#090d16] border border-slate-800 space-y-3 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Configured Retention Window:</span>
              <span className="text-white font-mono font-semibold">24 Hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Currently Stored Active Files:</span>
              <span className="text-slate-100 font-mono font-semibold">
                {metrics?.active_files_stored ?? 0} file(s)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Shredding Method:</span>
              <span className="text-slate-300 font-mono">Zero-fill overwrite + filesystem unlink</span>
            </div>
          </div>

          {purgeFeedback && (
            <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{purgeFeedback}</span>
            </div>
          )}

          <div className="pt-2">
            <button
              onClick={handlePurge}
              disabled={purging}
              className="px-5 py-2.5 rounded-lg bg-red-950/30 hover:bg-red-900/40 border border-red-800/40 text-red-300 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{purging ? "Executing Shredder..." : "Run Manual Retention Purge"}</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: Audits Queue */}
      {activeTab === "audits" && (
        <div className="rounded-xl border border-slate-800 bg-[#0c121e] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#090d16] text-slate-400 uppercase text-[10px] font-mono border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Target</th>
                  <th className="px-4 py-3.5">Contact</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Created</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {audits.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-12 text-center text-slate-500">
                      No audit requests currently in the queue.
                    </td>
                  </tr>
                ) : (
                  audits.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-900/40">
                      <td className="px-4 py-4 font-mono font-medium text-white">{a.target_url}</td>
                      <td className="px-4 py-4">
                        <div className="font-semibold text-slate-200">{a.contact_name}</div>
                        <div className="text-slate-400 text-[11px]">{a.contact_email}</div>
                        {a.organization && <div className="text-slate-500 text-[10px]">{a.organization}</div>}
                      </td>
                      <td className="px-4 py-4">
                        <select
                          value={a.status}
                          onChange={(e) => handleUpdateAuditStatus(a.id, e.target.value)}
                          className="bg-[#090d16] border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1 focus:outline-none focus:border-slate-500"
                        >
                          <option value="pending">Pending</option>
                          <option value="in_review">In Review</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </select>
                      </td>
                      <td className="px-4 py-4 text-slate-400">{formatDate(a.created_at)}</td>
                      <td className="px-4 py-4 text-right">
                        <button
                          onClick={() => openNotesModal(a.id)}
                          className="px-2.5 py-1 rounded bg-[#090d16] border border-slate-700 hover:border-slate-500 text-slate-300 text-xs inline-flex items-center gap-1 transition"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Notes</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Internal Notes Modal */}
      {activeNoteTarget && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="rounded-xl p-6 border border-slate-800 bg-[#0c121e] w-full max-w-lg space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-slate-400" />
                <span>Internal Notes</span>
              </h4>
              <button
                onClick={() => setActiveNoteTarget(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800"
              >
                Close
              </button>
            </div>

            {/* Existing Notes */}
            <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
              {noteLoading ? (
                <div className="text-center py-4 text-xs text-slate-500">Loading notes...</div>
              ) : notesList.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">No notes recorded yet.</div>
              ) : (
                notesList.map((n) => (
                  <div key={n.id} className="p-3 rounded-lg bg-[#090d16] border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between text-slate-400 text-[10px]">
                      <span className="font-semibold text-slate-300">{n.author}</span>
                      <span>{formatDate(n.created_at)}</span>
                    </div>
                    <p className="text-slate-200">{n.note}</p>
                  </div>
                ))
              )}
            </div>

            {/* Add Note Form */}
            <form onSubmit={handleAddNote} className="space-y-3 pt-2 border-t border-slate-800">
              <textarea
                rows={2}
                placeholder="Enter internal comment, client communication, or re-test scope..."
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#090d16] border border-slate-700 text-white text-xs focus:outline-none focus:border-slate-500"
                required
              />
              <button
                type="submit"
                className="w-full py-2 rounded-lg bg-slate-100 hover:bg-white text-slate-900 font-semibold text-xs flex items-center justify-center gap-1.5 transition"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Save Note</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
