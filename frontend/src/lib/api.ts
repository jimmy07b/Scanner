import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
const API_ROOT = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/api\/v1\/?$/, "");

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
  total_file_scans: number;
  total_url_scans: number;
  threats_flagged: number;
  audit_requests_count: number;
  pending_audits: number;
  total_revenue_inr: number;
  active_files_stored: number;
}

export const api = {
  // 3-Engine Asynchronous Job Pipeline
  async startUrlCheck(url: string, authorized: boolean): Promise<ScanJobResponse> {
    const res = await axios.post(`${API_ROOT}/api/scans/url`, { url, authorized });
    return res.data;
  },

  async startWebsiteAudit(url: string, authorized: boolean): Promise<ScanJobResponse> {
    const res = await axios.post(`${API_ROOT}/api/scans/website`, { url, authorized });
    return res.data;
  },

  async startFileScan(file: File, authorized: boolean): Promise<ScanJobResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("authorized", String(authorized));

    const res = await axios.post(`${API_ROOT}/api/scans/file`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async getScanJob(scanId: string): Promise<ScanResult> {
    const res = await axios.get(`${API_ROOT}/api/scans/${scanId}`);
    return res.data;
  },

  // Legacy compatibility scans
  async scanFile(file: File, authorized: boolean): Promise<ScanResult> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("authorized", String(authorized));

    const res = await axios.post(`${API_BASE}/scan/file`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async scanUrl(url: string, authorized: boolean): Promise<ScanResult> {
    const res = await axios.post(`${API_BASE}/scan/url`, { url, authorized });
    return res.data;
  },

  async getScanResult(id: string): Promise<ScanResult> {
    // Try the scan job endpoint first, fallback to scan result
    try {
      const res = await axios.get(`${API_ROOT}/api/scans/${id}`);
      return res.data;
    } catch {
      const res = await axios.get(`${API_BASE}/scan/${id}`);
      return res.data;
    }
  },

  async shredFile(scanId: string): Promise<{ message: string; shredded: boolean }> {
    const res = await axios.post(`${API_BASE}/scan/${scanId}/shred`);
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
    const res = await axios.post(`${API_BASE}/audits/request`, data);
    return res.data;
  },

  async getAuditRequest(id: string): Promise<AuditRequest> {
    const res = await axios.get(`${API_BASE}/audits/${id}`);
    return res.data;
  },

  async payAuditRequest(id: string, payment_method = "card"): Promise<any> {
    const res = await axios.post(`${API_BASE}/audits/${id}/payment`, {
      audit_request_id: id,
      payment_method,
    });
    return res.data;
  },

  // Reports
  async getReport(id: string): Promise<any> {
    const res = await axios.get(`${API_BASE}/reports/${id}`);
    return res.data;
  },

  getPrintableExportUrl(id: string): string {
    return `${API_BASE}/reports/${id}/export`;
  },

  // Admin
  async adminLogin(email: string, password: string): Promise<{ access_token: string; token_type: string; user_email: string }> {
    const res = await axios.post(`${API_BASE}/admin/login`, { email, password });
    return res.data;
  },

  async getAdminMetrics(token: string): Promise<AdminMetrics> {
    const res = await axios.get(`${API_BASE}/admin/metrics`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminScans(token: string): Promise<any[]> {
    const res = await axios.get(`${API_BASE}/admin/scans`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminAudits(token: string): Promise<AuditRequest[]> {
    const res = await axios.get(`${API_BASE}/admin/audits`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async updateAuditStatus(id: string, data: { status?: string; payment_status?: string }, token: string): Promise<AuditRequest> {
    const res = await axios.patch(`${API_BASE}/admin/audits/${id}`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async createAdminNote(data: { target_type: string; target_id: string; note: string }, token: string): Promise<any> {
    const res = await axios.post(`${API_BASE}/admin/notes`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async getAdminNotes(target_type: string, target_id: string, token: string): Promise<any[]> {
    const res = await axios.get(`${API_BASE}/admin/notes/${target_type}/${target_id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },

  async purgeExpiredFiles(token: string): Promise<any> {
    const res = await axios.post(`${API_BASE}/admin/retention/purge`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  },
};
