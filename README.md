# AegisScan — Privacy-First Static Security Scanning & Website Audit Platform

AegisScan is a production-ready cybersecurity MVP platform designed to provide automated static security inspection for files (PDFs, Office documents, images, archives) and website HTTP hygiene audits, with a paid manual audit flow (₹1,999) for deeper web app defense.

---

## 🛡️ Core Principles & Architecture

1. **Zero Execution Guarantee**: Uploaded files are inspected purely through static parsers (magic bytes, PDF stream tokens, OOXML relationships, EXIF metadata, archive structures) in memory. No binaries or scripts are executed.
2. **Privacy First (24-Hour Auto-Purge)**: All uploads are permanently overwritten and shredded after 24 hours. Users can also immediately shred files on-demand directly from their report page.
3. **Mandatory Authorization**: Users must confirm ownership or written authorization before analyzing any target file or website.

---

## 🗂️ Platform Capabilities

### 1. Free File Static Analysis
- **PDF Documents**: Checks for `/JavaScript`, `/JS`, `/Launch` actions, embedded executable attachments, and suspicious hyperlinks.
- **Office Documents (DOCX, XLSX, PPTX)**: Detects VBA macros (`vbaProject.bin`), external template injection (`TargetMode="External"`), and OLE objects.
- **Images (PNG, JPG, WEBP)**: Scrubs EXIF metadata, flags GPS location privacy risks, identifies editing software, and detects appended data beyond EOF.
- **ZIP Archives**: Safely walks archives, catches Zip Slip directory traversal (`../`), decompression bombs, and flags dangerous executable extensions (`.exe`, `.bat`, `.ps1`, `.scr`).
- **Text & Secrets**: Inspects source files and logs for exposed private cryptographic keys (RSA/EC/SSH) and cloud access tokens.

### 2. Free Website Hygiene Audit
- **Transport Security**: Verifies HTTPS enforcement and HTTP-to-HTTPS redirect.
- **Security Headers**: Audits `Strict-Transport-Security` (HSTS), `Content-Security-Policy` (CSP), `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, and `Permissions-Policy`.
- **Cookie Security**: Flags cookies missing `Secure`, `HttpOnly`, or `SameSite` flags.
- **Information Leaks**: Detects server banners (`Server`, `X-Powered-By`) and public administrative routes in `robots.txt`.

### 3. Advanced Website Security Audit (₹1,999)
- Human-led security assessment conducted by senior security engineers.
- Comprehensive TLS cipher review, custom CSP policy design, and reconnaissance review.
- Executive PDF deliverable with prioritized developer remediation steps.
- **1 Free Retest** within 30 days of implementing fixes.

---

## 🚀 Quickstart Guide

### Option A: Local Development (Instant SQLite Fallback)

#### 1. Backend (FastAPI + Python 3.11+)
```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API will be accessible at: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Default Admin Account: `admin@aegisscan.com` / `AegisScan2026!Secure`

#### 2. Frontend (Next.js 14 + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```
- Web Application will be live at: `http://localhost:3000`

---

### Option B: Full Production Docker Deployment

```bash
docker-compose up --build -d
```

Services started:
- `nginx`: Reverse proxy on `http://localhost` (port 80)
- `frontend`: Next.js web application on `http://localhost:3000`
- `backend`: FastAPI API service on `http://localhost:8000`
- `postgres`: PostgreSQL 16 database on port 5432
- `redis`: Redis 7 caching and queue broker on port 6379

---

## 🧪 Automated Testing

Run the full unit and integration test suite:

```bash
python -m pytest backend/tests/ -v
```

All 9 test suites verify:
- Clean file analysis
- Sensitive credential / private key detection
- ZIP archive traversal and executable detection
- PDF JavaScript stream detection
- Website URL normalization & header audits
- Health check endpoints
- Unauthorized scanning rejection
- Advanced audit booking & payment simulation workflow
- Admin authentication & JWT token generation

---

## 🔒 Security Credentials

- **Admin Login**: `/admin`
- **Default Email**: `admin@aegisscan.com`
- **Default Password**: `AegisScan2026!Secure`
*(Remember to update `SECRET_KEY` and admin credentials via environment variables in production)*
