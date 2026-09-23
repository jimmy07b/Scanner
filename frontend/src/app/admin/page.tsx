"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Lock,
  Trash2,
  CheckCircle,
  AlertTriangle,
  LogOut,
  RefreshCw,
  ExternalLink,
  MessageSquare,
  Send,
  Shield,
  Activity,
  Layers,
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
        <div className="rounded-2xl p-8 border border-[#1a293e] bg-[#0d1522] shadow-2xl">
          <div className="w-12 h-12 rounded-xl bg-[#070b12] border border-[#71C9CE]/40 flex items-center justify-center text-[#71C9CE] mx-auto mb-4">
            <Lock className="w-6 h-6 text-[#71C9CE]" />
          </div>
          <h2 className="text-xl font-bold text-white text-center font-sans">RootLayer Administration</h2>
          <p className="text-xs text-slate-400 text-center mt-1">
            Sign in to inspect system telemetry, live scans feed, and retention storage.
          </p>

          <form onSubmit={handleLogin} className="mt-8 space-y-4">
            <div>
              <label className="text-xs font-semibold text-[#CBF1F5] block mb-1 font-mono">
                Admin Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@rootlayer.io"
                className="w-full px-4 py-2.5 rounded-lg bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] text-sm focus:outline-none focus:border-[#71C9CE]"
                required
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-[#CBF1F5] block mb-1 font-mono">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] text-sm focus:outline-none focus:border-[#71C9CE]"
                required
              />
            </div>

            {loginError && (
              <div className="p-3 rounded-lg bg-red-950/30 border border-red-500/40 text-red-300 text-xs flex items-center gap-2 font-mono">
                <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
                <span>{loginError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loginLoading}
              className="w-full py-3 rounded-lg bg-[#71C9CE] hover:bg-[#A6E3E9] text-[#070b12] font-bold text-sm shadow-md shadow-[#71C9CE]/25 transition disabled:opacity-50 mt-2"
            >
              {loginLoading ? "Authenticating..." : "Sign In to Operations"}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-[#1a293e] text-[11px] text-slate-500 text-center font-mono">
            Protected Administrative Gateway • Authorized Personnel Only
          </div>
        </div>
      </div>
    );
  }

  // 2. Authenticated Admin Dashboard
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8 font-sans">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-[#1a293e] gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#71C9CE] animate-pulse" />
            <span className="text-xs font-mono text-[#A6E3E9] uppercase tracking-wider font-semibold">
              Platform Telemetry &amp; Operations
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            RootLayer Administration
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadDashboardData}
            disabled={dataLoading}
            className="p-2.5 rounded-lg bg-[#0d1522] border border-[#1a293e] text-slate-400 hover:text-[#E3FDFD] hover:border-[#71C9CE] transition"
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-4 h-4 text-[#71C9CE] ${dataLoading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-[#1a293e] bg-[#0d1522] text-slate-400 hover:text-red-400 hover:border-red-500/40 text-xs font-semibold font-mono transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Operational KPI Cards */}
      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-xl p-5 border border-[#1a293e] bg-[#0d1522] space-y-1 shadow-md">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Total Security Scans</div>
            <div className="text-3xl font-extrabold text-[#E3FDFD] font-mono">{metrics.total_scans}</div>
            <div className="text-[11px] text-slate-400">
              {metrics.total_website_scans || 0} Websites • {metrics.total_url_scans} URLs • {metrics.total_file_scans} Files
            </div>
          </div>

          <div className="rounded-xl p-5 border border-[#1a293e] bg-[#0d1522] space-y-1 shadow-md">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Threats &amp; High Risk</div>
            <div className="text-3xl font-extrabold text-red-400 font-mono">
              {metrics.threats_flagged}
            </div>
            <div className="text-[11px] text-slate-400">High / Critical risk detections</div>
          </div>

          <div className="rounded-xl p-5 border border-[#1a293e] bg-[#0d1522] space-y-1 shadow-md">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Retained File Storage</div>
            <div className="text-3xl font-extrabold text-[#CBF1F5] font-mono">
              {metrics.active_files_stored}
            </div>
            <div className="text-[11px] text-slate-400">Uploads under retention window</div>
          </div>

          <div className="rounded-xl p-5 border border-[#1a293e] bg-[#0d1522] space-y-1 shadow-md">
            <div className="text-xs uppercase font-semibold text-slate-400 font-mono">Detection Engine Suite</div>
            <div className="text-3xl font-extrabold text-[#71C9CE] font-mono">
              3 / 3 Active
            </div>
            <div className="text-[11px] text-slate-400">Website, URL Threat, Static File engines</div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-[#1a293e] gap-6 text-xs sm:text-sm font-semibold font-mono">
        <button
          onClick={() => setActiveTab("scans")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "scans"
              ? "border-[#71C9CE] text-[#E3FDFD]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Live Scan Feed ({scans.length})
        </button>
        <button
          onClick={() => setActiveTab("retention")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "retention"
              ? "border-[#71C9CE] text-[#E3FDFD]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          File Retention &amp; Storage
        </button>
        <button
          onClick={() => setActiveTab("audits")}
          className={`pb-3 border-b-2 transition ${
            activeTab === "audits"
              ? "border-[#71C9CE] text-[#E3FDFD]"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Audit Requests ({audits.length})
        </button>
      </div>

      {/* TAB 1: Live Scan Feed */}
      {activeTab === "scans" && (
        <div className="rounded-xl border border-[#1a293e] bg-[#0d1522] overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#070b12] text-[#CBF1F5] uppercase text-[10px] font-mono border-b border-[#1a293e]">
                <tr>
                  <th className="px-4 py-3.5">Engine</th>
                  <th className="px-4 py-3.5">Target</th>
                  <th className="px-4 py-3.5">Risk Score</th>
                  <th className="px-4 py-3.5">Verdict</th>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5 text-right">Report Output</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1a293e]/60">
                {scans.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-slate-500 font-mono">
                      No security scans recorded yet.
                    </td>
                  </tr>
                ) : (
                  scans.map((s) => (
                    <tr key={s.id} className="hover:bg-[#131e2e]/50 transition-colors">
                      <td className="px-4 py-3.5">
                        <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-[#070b12] text-[#A6E3E9] border border-[#1a293e] uppercase font-semibold">
                          {s.scan_type}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-white max-w-xs truncate" title={s.target_name}>
                        {s.target_name}
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-[#E3FDFD]">{s.risk_score} / 100</td>
                      <td className="px-4 py-3.5">
                        <RiskBadge status={s.status} size="sm" />
                      </td>
                      <td className="px-4 py-3.5 text-slate-400 font-mono text-[11px]">{formatDate(s.created_at)}</td>
                      <td className="px-4 py-3.5 text-right">
                        <Link
                          href={`/reports/${s.id}`}
                          className="px-2.5 py-1 rounded bg-[#070b12] border border-[#1a293e] hover:border-[#71C9CE] text-[#71C9CE] hover:text-[#E3FDFD] inline-flex items-center gap-1.5 font-mono text-xs font-semibold transition"
                        >
                          <span>View Report</span>
                          <ExternalLink className="w-3 h-3 text-[#71C9CE]" />
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
        <div className="rounded-xl p-6 sm:p-8 border border-[#1a293e] bg-[#0d1522] space-y-6 max-w-3xl shadow-xl">
          <div>
            <h3 className="text-base font-bold text-white">Storage Lifecycle &amp; Retention Policy</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              RootLayer statically inspects files and enforces an automated retention policy to eliminate indefinite storage of uploaded payloads.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#070b12] border border-[#1a293e] space-y-3 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Configured Retention Window:</span>
              <span className="text-[#E3FDFD] font-semibold">24 Hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Currently Stored Active Files:</span>
              <span className="text-[#CBF1F5] font-semibold">
                {metrics?.active_files_stored ?? 0} file(s)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Shredding Method:</span>
              <span className="text-[#71C9CE]">Zero-fill overwrite + filesystem unlink</span>
            </div>
          </div>

          {purgeFeedback && (
            <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2 font-mono">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{purgeFeedback}</span>
            </div>
          )}

          <div className="pt-2">
            <button
              onClick={handlePurge}
              disabled={purging}
              className="px-5 py-2.5 rounded-lg bg-red-950/30 hover:bg-red-900/40 border border-red-800/40 text-red-300 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50 font-mono"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{purging ? "Executing Shredder..." : "Run Manual Retention Purge"}</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: Audits Queue */}
      {activeTab === "audits" && (
        <div className="rounded-xl border border-[#1a293e] bg-[#0d1522] overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#070b12] text-[#CBF1F5] uppercase text-[10px] font-mono border-b border-[#1a293e]">
                <tr>
                  <th className="px-4 py-3.5">Target</th>
                  <th className="px-4 py-3.5">Contact</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Created</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1a293e]/60">
                {audits.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-12 text-center text-slate-500 font-mono">
                      No audit requests currently in the queue.
                    </td>
                  </tr>
                ) : (
                  audits.map((a) => (
                    <tr key={a.id} className="hover:bg-[#131e2e]/50 transition-colors">
                      <td className="px-4 py-4 font-mono font-bold text-white">{a.target_url}</td>
                      <td className="px-4 py-4">
                        <div className="font-semibold text-slate-200">{a.contact_name}</div>
                        <div className="text-slate-400 text-[11px]">{a.contact_email}</div>
                        {a.organization && <div className="text-[#A6E3E9] text-[10px]">{a.organization}</div>}
                      </td>
                      <td className="px-4 py-4">
                        <select
                          value={a.status}
                          onChange={(e) => handleUpdateAuditStatus(a.id, e.target.value)}
                          className="bg-[#070b12] border border-[#1a293e] text-[#CBF1F5] text-xs rounded-lg px-2.5 py-1 focus:outline-none focus:border-[#71C9CE] font-mono"
                        >
                          <option value="pending">Pending</option>
                          <option value="in_review">In Review</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </select>
                      </td>
                      <td className="px-4 py-4 text-slate-400 font-mono text-[11px]">{formatDate(a.created_at)}</td>
                      <td className="px-4 py-4 text-right">
                        <button
                          onClick={() => openNotesModal(a.id)}
                          className="px-2.5 py-1 rounded bg-[#070b12] border border-[#1a293e] hover:border-[#71C9CE] text-[#CBF1F5] hover:text-[#E3FDFD] text-xs inline-flex items-center gap-1 font-mono transition"
                        >
                          <MessageSquare className="w-3 h-3 text-[#71C9CE]" />
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
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="rounded-2xl p-6 border border-[#1a293e] bg-[#0d1522] w-full max-w-lg space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1a293e] pb-3">
              <h4 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
                <MessageSquare className="w-4 h-4 text-[#71C9CE]" />
                <span>Internal Notes</span>
              </h4>
              <button
                onClick={() => setActiveNoteTarget(null)}
                className="text-slate-400 hover:text-white text-xs px-2.5 py-1 rounded-lg bg-[#070b12] border border-[#1a293e] hover:border-[#71C9CE] font-mono transition"
              >
                Close
              </button>
            </div>

            {/* Existing Notes */}
            <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
              {noteLoading ? (
                <div className="text-center py-4 text-xs text-slate-500 font-mono">Loading notes...</div>
              ) : notesList.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500 font-mono">No notes recorded yet.</div>
              ) : (
                notesList.map((n) => (
                  <div key={n.id} className="p-3 rounded-lg bg-[#070b12] border border-[#1a293e] text-xs space-y-1">
                    <div className="flex justify-between text-slate-400 text-[10px] font-mono">
                      <span className="font-semibold text-[#71C9CE]">{n.author}</span>
                      <span>{formatDate(n.created_at)}</span>
                    </div>
                    <p className="text-slate-200">{n.note}</p>
                  </div>
                ))
              )}
            </div>

            {/* Add Note Form */}
            <form onSubmit={handleAddNote} className="space-y-3 pt-2 border-t border-[#1a293e]">
              <textarea
                rows={2}
                placeholder="Enter internal comment, client communication, or re-test scope..."
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#070b12] border border-[#1a293e] text-[#E3FDFD] text-xs focus:outline-none focus:border-[#71C9CE]"
                required
              />
              <button
                type="submit"
                className="w-full py-2.5 rounded-lg bg-[#71C9CE] hover:bg-[#A6E3E9] text-[#070b12] font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-[#71C9CE]/25 transition"
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
