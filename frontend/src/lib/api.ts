import axios from "axios";

// Helper to resolve active API root and base:
// In the browser, use relative paths so requests are reverse-proxied transparently
// through Next.js rewrites to the backend on the same origin (no CORS issues, no adblock blocks).
// On the server, fallback to BACKEND_URL or NEXT_PUBLIC_API_URL or local backend.
export const getApiRoot = (): string => {
  if (typeof window !== "undefined") {
    return "";
  }
  const raw = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  return raw.replace(/\/api\/v1\/?$/, "").replace(/\/api\/?$/, "");
};

export const getApiBase = (): string => {
  if (typeof window !== "undefined") {
    return "/api/v1";
  }
  const raw = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
  return raw.endsWith("/api/v1") ? raw : `${raw.replace(/\/+$/, "")}/api/v1`;
};

export interface Finding {
  id?: string;
  finding_key?: string;
  title: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  confidence?: "high" | "medium" | "low";
  category: string;
  evidence?: string | string[];
  recommendation?: string;
}

export interface ScanJobResponse {
  scan_id: string;
  target: string;
  scan_type: "url_check" | "website" | "file";
  status: "queued" | "running" | "completed" | "failed";
  stage: string;
  progress: number;
  message?: string;
  created_at: string;
}

export interface ScanResult {
  id: string;
  scan_id?: string;
  target?: string;
  scan_type: "url_check" | "website" | "file" | "url";
  target_name: string;
  status: "queued" | "running" | "completed" | "failed" | "clean" | "low" | "medium" | "high" | "critical";
  stage?: string;
  progress?: number;
  verdict?: "safe" | "suspicious" | "phishing-like" | "redirect-heavy" | "malware-linked" | "unreachable" | "clean" | "low" | "medium" | "high" | "critical";
  risk_score: number;
  summary: string;
  raw_metadata: Record<string, any>;
  created_at: string;
  findings: Finding[];
  upload_id?: string;
  checks?: Record<string, any>;
  passed_checks?: string[];
  collected_data?: Record<string, any>;
  evidence_collected?: boolean;
  scope_and_method?: Record<string, any>;
  observed_technologies?: Record<string, any>;
  technology_profile?: Record<string, any>;
  methodology_notes?: Record<string, any>;
  executive_summary?: string;
}

export interface AuditRequest {
  id: string;
  target_url: string;
  contact_name: string;
  contact_email: string;
  organization?: string;
  scope_notes?: string;
  payment_status: string;
  amount_inr: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AdminMetrics {
  total_scans: number;
  total_website_scans?: number;
  total_file_scans?: number;
  total_url_scans?: number;
  threats_flagged?: number;
  audit_requests_count?: number;
  pending_audits?: number;
  total_revenue_inr?: number;
  active_files_stored?: number;
  total_findings?: number;
  total_audits?: number;
  recent_scans?: ScanResult[];
  recent_audits?: AuditRequest[];
}

export const api = {
  // 3-Engine Asynchronous Job Pipeline
  async startUrlCheck(url: string, authorized: boolean): Promise<ScanJobResponse> {
    const root = getApiRoot();
    const res = await axios.post(`${root}/api/scans/url`, { url, authorized });
    return res.data;
  },

  async startWebsiteAudit(url: string, authorized: boolean): Promise<ScanJobResponse> {
    const root = getApiRoot();
    const res = await axios.post(`${root}/api/scans/website`, { url, authorized });
    return res.data;
  },

  async startFileScan(file: File, authorized: boolean): Promise<ScanJobResponse> {
    const root = getApiRoot();
    const formData = new FormData();
    formData.append("file", file);
    formData.append("authorized", String(authorized));

    const res = await axios.post(`${root}/api/scans/file`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async getScanJob(scanId: string): Promise<ScanResult> {
    const root = getApiRoot();
    const res = await axios.get(`${root}/api/scans/${scanId}`);
    return res.data;
  },

  // Legacy compatibility scans
  async scanFile(file: File, authorized: boolean): Promise<ScanResult> {
    const base = getApiBase();
    const formData = new FormData();
    formData.append("file", file);
    formData.append("authorized", String(authorized));

    const res = await axios.post(`${base}/scan/file`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async scanUrl(url: string, authorized: boolean): Promise<ScanResult> {
    const base = getApiBase();
    const res = await axios.post(`${base}/scan/url`, { url, authorized });
    return res.data;
  },

  async getScanResult(id: string): Promise<ScanResult> {
    const root = getApiRoot();
    const base = getApiBase();
    try {
      const res = await axios.get(`${root}/api/scans/${id}`);
      return res.data;
    } catch {
      const res = await axios.get(`${base}/scan/${id}`);
      return res.data;
    }
  },

  async shredFile(scanId: string): Promise<{ message: string; shredded: boolean }> {
    const base = getApiBase();
    const res = await axios.post(`${base}/scan/${scanId}/shred`);
    return res.data;
  },

  // Audits (₹1,999)
  async createAuditRequest(data: {
    target_url: string;
    contact_name: string;
    contact_email: string;
    organization?: string;
    scope_notes?: string;
    authorized: boolean;
  }): Promise<AuditRequest> {
    const base = getApiBase();
    const res = await axios.post(`${base}/audits/request`, data);
    return res.data;
  },

  async getAuditRequest(id: string): Promise<AuditRequest> {
    const base = getApiBase();
    const res = await axios.get(`${base}/audits/${id}`);
    return res.data;
  },

  async payAuditRequest(id: string, payment_method = "card"): Promise<any> {
    const base = getApiBase();
    const res = await axios.post(`${base}/audits/${id}/payment`, {
      audit_request_id: id,
      payment_method,
    });
    return res.data;
  },

  // Reports
  async getReport(id: string): Promise<any> {
    const base = getApiBase();
    const res = await axios.get(`${base}/reports/${id}`);
    return res.data;
  },

  getPrintableExportUrl(id: string): string {
    const base = getApiBase();
    return `${base}/reports/${id}/export`;
  },

  // Admin
  async adminLogin(email: string, password: string): Promise<{ access_token: string; token_type: string; user_email: string }> {
    const base = getApiBase();
    const res = await axios.post(`${base}/admin/login`, { email, password });
    return res.data;
  },

  async getAdminMetrics(token: string): Promise<AdminMetrics> {
    const base = getApiBase();
    const res = await axios.get(`${base}/admin/metrics`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminScans(token: string): Promise<any[]> {
    const base = getApiBase();
    const res = await axios.get(`${base}/admin/scans`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminAudits(token: string): Promise<AuditRequest[]> {
    const base = getApiBase();
    const res = await axios.get(`${base}/admin/audits`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async updateAuditStatus(id: string, data: { status?: string; payment_status?: string }, token: string): Promise<AuditRequest> {
    const base = getApiBase();
    const res = await axios.patch(`${base}/admin/audits/${id}`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async createAdminNote(data: { target_type: string; target_id: string; note: string }, token: string): Promise<any> {
    const base = getApiBase();
    const res = await axios.post(`${base}/admin/notes`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminNotes(target_type: string, target_id: string, token: string): Promise<any[]> {
    const base = getApiBase();
    const res = await axios.get(`${base}/admin/notes/${target_type}/${target_id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async purgeExpiredFiles(token: string): Promise<any> {
    const base = getApiBase();
    const res = await axios.post(`${base}/admin/retention/purge`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },
};
