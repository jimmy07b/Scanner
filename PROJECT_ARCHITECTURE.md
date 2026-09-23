# RootLayer / AegisScan — Project Architecture & Technology Stack Specification

This document provides a complete technical blueprint of **RootLayer** (formerly AegisScan), including the full directory structure, programming languages, frameworks, security scanning engines, algorithms, and production cloud infrastructure.

---

## 1. High-Level System Architecture

RootLayer is an enterprise-grade, evidence-first cybersecurity assessment and passive reconnaissance platform. It operates under a strict **Zero Synthetic Findings / Evidence-First** standard: every metric, technology version, and finding originates exclusively from observed live network responses.

```
                              ┌────────────────────────────────────────────────────────┐
                              │                    Client Browser                      │
                              │           https://scanner-ywmt.vercel.app              │
                              └───────────────────────────┬────────────────────────────┘
                                                          │
                                     HTTPS REST / JSON    │ (CORS Enabled with regex)
                                                          ▼
                              ┌────────────────────────────────────────────────────────┐
                              │             FastAPI Backend API (Render)               │
                              │           https://scanner-mtxg.onrender.com            │
                              └───────┬───────────────────┬───────────────────┬────────┘
                                      │                   │                   │
                  ┌───────────────────┴───────┐   ┌───────┴───────┐   ┌───────┴───────────────┐
                  │ Engine 1: URL Threat      │   │ Engine 2:     │   │ Engine 3: Static File │
                  │ Reputation & Redirects    │   │ Website Audit │   │ Inspection & Shredder │
                  └───────────────────────────┘   └───────┬───────┘   └───────────────────────┘
                                                          │
                                          ┌───────────────┴───────────────┐
                                          │ Phase 1: Passive Recon        │
                                          │ - DNS (SPF, DMARC, CAA)       │
                                          │ - TLS Certificate Chains      │
                                          │ - 6 Defensive Headers         │
                                          │ - Cookie Security Flags       │
                                          │ - Technology Fingerprinting   │
                                          ├───────────────────────────────┤
                                          │ Phase 2: Security Checks      │
                                          │ - Verified Flaws (Evidence)   │
                                          │ - Unrated Hardening Notes     │
                                          │ - 99% Secure Baseline Posture │
                                          └───────────────────────────────┘
```

---

## 2. Programming Languages Used

| Language | Version / Standard | Area of Usage |
| :--- | :--- | :--- |
| **Python** | `Python 3.11+ / 3.14` | Backend API, asynchronous security engines, static file analysis, cryptography, DNS resolvers, socket TLS inspection. |
| **TypeScript** | `TypeScript 5.x` | Frontend App Router, strict type safety, data models, API client, and component interfaces. |
| **JavaScript** | `ECMAScript 2022 / Node 20` | Next.js configuration, Tailwind plugins, PostCSS runtime. |
| **HTML5 & Modern CSS** | `CSS3 / TailwindCSS 3.4` | Dark enterprise UI layout, GitHub/HackerOne document styling, responsive layouts. |
| **SQL** | `SQL:2016` (SQLite / Postgres) | Database models, scan jobs, uploads tracking, audit requests, user roles. |
| **Shell / PowerShell** | `PowerShell 7 / Bash` | Build automation, CLI management, E2E verification test suites. |
| **YAML** | `YAML 1.2` | Cloud deployment manifests (`render.yaml`, `docker-compose.yml`). |

---

## 3. Technology Stack & Dependencies

### Frontend (`/frontend`)
- **Core Framework**: [Next.js 14](https://nextjs.org/) (App Router, Server-side generation & client hydration)
- **UI Library**: [React 18](https://react.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) with custom dark enterprise color tokens (`#0e1117`, `#161b22`, zinc/slate scales)
- **Iconography**: [Lucide React](https://lucide.dev/) (Muted, professional stroke icons; zero flashy badges)
- **HTTP Client**: [Axios](https://axios-http.com/) (Configured with dynamic backend baseURL resolution)
- **Utilities**: `clsx`, `tailwind-merge`

### Backend (`/backend`)
- **Web Framework**: [FastAPI 0.110+](https://fastapi.tiangolo.com/) (Asynchronous Python framework)
- **ASGI Server**: [Uvicorn 0.28+](https://www.uvicorn.org/) with `httptools` and `uvloop`
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Database & ORM**: [SQLAlchemy 2.0 (asyncio)](https://www.sqlalchemy.org/) + [aiosqlite](https://github.com/omnilib/aiosqlite) (SQLite) / [asyncpg](https://github.com/MagicStack/asyncpg) (PostgreSQL)
- **Authentication & Cryptography**: `pyjwt` (HMAC-SHA256 JWT tokens), `bcrypt` (password hashing), Python `hashlib` (SHA-256, MD5, SHA-1)
- **Networking & Scraping**: [HTTPX 0.27+](https://www.python-httpx.org/) (Async HTTP/2 client), [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) with `lxml`, [dnspython](https://www.dnspython.org/) (DNS query records), [tldextract](https://github.com/john-kurkowski/tldextract)
- **Static File Inspection**:
  - `Pillow 10.2+` (Image dimension, aspect ratio, metadata, pixel bombs)
  - `pypdf 4.1+` (PDF embedded JavaScript `/JS` indicators, encryption, launch action inspection)
  - `openpyxl 3.1+` (Excel spreadsheet XML relationships and hidden macros)
  - `python-docx 1.1+` (Word document macro detection)
- **Test Framework**: `pytest 8.1+` & `pytest-asyncio 0.23+` (17/17 tests passing)

### Production Cloud Hosting
- **Frontend Hosting**: [Vercel](https://vercel.com/) (Global Edge CDN, auto HTTPS, CI/CD from GitHub)
- **Backend Hosting**: [Render](https://render.com/) (Linux Web Service container, auto HTTPS, background task concurrency)
- **Source Control**: [GitHub](https://github.com/jimmy07b/Scanner) (`main` branch automated deployment)

---

## 4. Complete Project Directory Structure

```
c:\Users\Bibesh Roy\Documents\Start up\
│
├── .gitignore                          # Comprehensive ignore rules (node_modules, caches, db, uploads)
├── README.md                           # Project introduction and quickstart
├── DEPLOYMENT.md                       # Complete Render + Vercel production hosting guide
├── PROJECT_ARCHITECTURE.md             # Complete architecture, languages, and technical specifications
├── docker-compose.yml                  # Local multi-container Docker specification (Postgres, Redis, Backend, Frontend, Nginx)
├── render.yaml                         # 1-Click Render.com deployment manifest
├── test_all_engines_e2e.py             # 5-Stage production verification & hardening test suite
│
├── nginx/
│   └── nginx.conf                      # Production reverse proxy & SSL termination configuration
│
├── backend/                            # FastAPI Python Backend Service
│   ├── Dockerfile                      # Production Docker container image for backend
│   ├── Procfile                        # Heroku/Railway process declaration
│   ├── requirements.txt                # Python production & test dependencies
│   ├── aegis_scan.db                   # Local SQLite database (gitignored)
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application setup, CORS regex, security headers middleware
│   │   │
│   │   ├── core/                       # Core infrastructure & security
│   │   │   ├── config.py               # Environment configuration (Pydantic BaseSettings, CORS parsing)
│   │   │   ├── database.py             # Async SQLAlchemy engine & session factory
│   │   │   ├── security.py             # JWT token handling, password hashing, sliding-window rate limiter
│   │   │   └── storage.py              # Cryptographic file storage manager & hash calculator
│   │   │
│   │   ├── models/                     # SQLAlchemy Database Entities
│   │   │   └── models.py               # User, Upload, ScanResult, Finding, AuditRequest models
│   │   │
│   │   ├── schemas/                    # Pydantic Request & Response DTOs
│   │   │   └── schemas.py              # Validation schemas for scans, jobs, reports, auth, admin metrics
│   │   │
│   │   ├── api/v1/                     # REST API Routers
│   │   │   ├── admin.py                # Role-gated admin endpoints, metric analytics, scan deletion
│   │   │   ├── audits.py               # Deep manual audit request creation & INR payment tracking
│   │   │   ├── reports.py              # Printable HTML/PDF report export & JSON telemetry endpoints
│   │   │   ├── scan.py                 # Synchronous direct file & URL scan endpoints
│   │   │   └── scans.py                # Asynchronous 3-engine job pipeline endpoints (POST / GET by ID)
│   │   │
│   │   └── services/                   # Security Analysis Engines & Business Logic
│   │       ├── cms_fingerprinter.py    # Wappalyzer-style CMS, web server, and technology stack profiler
│   │       ├── file_scanner.py         # Static file parser (PDF, Office, Images, Archives)
│   │       ├── report_builder.py       # Assembles evidence-only findings, passed checks, and 99% posture
│   │       ├── report_service.py       # Printable standalone HTML report generator
│   │       ├── retention_service.py    # Cryptographic file shredder (overwrites with random bytes)
│   │       ├── risk_engine.py          # Deterministic heuristic scoring engine
│   │       ├── scan_queue.py           # In-memory asynchronous background task execution queue
│   │       ├── url_auditor.py          # HTTP transport, redirect chain, and header inspection
│   │       ├── url_checker.py          # Typosquatting, brand impersonation, and URL obfuscation engine
│   │       └── website_auditor.py      # Full 4-Phase passive recon & OWASP security verification engine
│   │
│   └── tests/                          # Automated Pytest Suite (17 Tests)
│       ├── test_api.py                 # Healthcheck, authentication, audit requests, rate limiting
│       ├── test_cms_fingerprinter.py   # WordPress, Shopify, and custom Jamstack detection
│       ├── test_engines.py             # URL checker, brand impersonation, website auditor
│       └── test_scanners.py            # Static file scanner, credentials leak, PDF JS, zip slip
│
└── frontend/                           # Next.js 14 TypeScript Frontend Application
    ├── Dockerfile                      # Multi-stage production container build (Alpine Node 20)
    ├── package.json                    # Dependencies & scripts (`dev`, `build`, `start`, `lint`)
    ├── next.config.js                  # Dynamic API reverse proxy rewrites (BACKEND_URL resolution)
    ├── tailwind.config.js              # Theme tokens (zinc/slate scales, monospace typography)
    ├── tsconfig.json                   # Strict TypeScript compiler options
    ├── vercel.json                     # Vercel deployment framework preset
    │
    ├── public/                         # Static assets, branding shapes, illustrations
    │   ├── hero-cyber-bg.jpg
    │   └── shapes/
    │
    └── src/
        ├── lib/
        │   ├── api.ts                  # Axios API SDK (job creation, polling, report fetching, shredding)
        │   └── utils.ts                # Date formatters, file size formatters, class merges
        │
        ├── components/                 # Reusable UI Components
        │   ├── Navbar.tsx              # Unlinked admin, clean enterprise branding
        │   ├── Footer.tsx              # Platform links, privacy policy, methodology statement
        │   ├── FindingsList.tsx        # Bug bounty evidence code blocks and copyable remediations
        │   ├── RiskBadge.tsx           # Muted enterprise status pills (no flashy neon pulses)
        │   ├── ScanPipelineTracker.tsx # Linear progress bar, connected pipeline, '!' scope note, live log
        │   └── ScoreGauge.tsx          # Neutral SVG progress indicator
        │
        └── app/                        # Next.js App Router Pages
            ├── layout.tsx              # Root HTML wrapper, metadata, global styles, Navbar & Footer
            ├── globals.css             # Global dark theme CSS, scrollbars, typography
            ├── page.tsx                # Main workstation with hero & unified 3-engine tab switcher
            ├── admin/page.tsx          # Protected admin panel with telemetry metrics and audit requests
            ├── audit-request/page.tsx  # Deep manual security assessment request flow
            ├── pricing/page.tsx        # Transparent pricing for manual penetration testing (₹1,999)
            ├── privacy/page.tsx        # 24h retention and zero code execution privacy guarantees
            ├── terms/page.tsx          # Non-destructive scanning authorization terms of service
            │
            ├── reports/
            │   └── [id]/page.tsx       # Document-style Bug Bounty / Pentest Assessment Report
            │
            └── scan/                   # Focused Scan Initiation Pages
                ├── website/page.tsx    # Live Website Security Audit form
                ├── url/page.tsx        # URL Threat & Brand Impersonation form
                └── file/page.tsx       # Static File Inspection drag-and-drop form
```

---

## 5. Security Engines & Analysis Modules

### Engine 1: URL Threat & Reputation Check
*   **Target Scope**: Bare domains, full URLs, redirect paths, suspicious links.
*   **Brand Impersonation**: Uses normalized Levenshtein edit distance and token boundaries to detect phishing targets impersonating major brands (PayPal, Google, Apple, Microsoft, Amazon, Netflix, Banking).
*   **Obfuscation Detection**: Identifies embedded credential syntax (`http://user:pass@evil.com`), raw hexadecimal or numerical IP hosts, and Punycode homoglyph tricks (`xn--...`).
*   **Redirect Tracking**: Follows up to 10 HTTP redirects without code execution, detecting cross-domain hops and cloak forwarding.

### Engine 2: Live Website Security Audit
*   **Phase 1: Passive Reconnaissance (Presented First in Reports)**:
    *   **DNS Security**: Queries A/AAAA records, MX mail exchanges, SPF configuration, DMARC policy enforcement (`p=reject`/`p=quarantine`/`p=none`), and CAA certificate issuer authorization.
    *   **TLS Telemetry**: Measures handshake parameters, TLS protocol versions (TLS 1.2, TLS 1.3), cipher suites, certificate issuer authority, and exact remaining validity days.
    *   **6 Essential HTTP Security Headers**:
        1. `Strict-Transport-Security` (HSTS max-age, includeSubDomains, preload)
        2. `Content-Security-Policy` (CSP presence and directives)
        3. `X-Frame-Options` (Clickjacking prevention: DENY / SAMEORIGIN)
        4. `X-Content-Type-Options` (MIME-sniffing prevention: nosniff)
        5. `Referrer-Policy` (strict-origin-when-cross-origin)
        6. `Permissions-Policy` (Camera, microphone, geolocation restrictions)
    *   **Cookie Security Audit**: Evaluates `Secure`, `HttpOnly`, and `SameSite` (Strict/Lax/None) attributes on all `Set-Cookie` headers.
    *   **Sensitive Surface Probes**: Safe passive checks against `robots.txt`, `sitemap.xml`, `security.txt` (RFC 9116), and `.well-known` endpoints.
*   **Phase 2: Technology & CMS Fingerprinting**:
    *   Inspects meta generators, header banners, script asset paths, cookie namespaces, and DOM patterns.
    *   Categorizes Web Servers (Nginx, Apache, LiteSpeed, Caddy, Cloudflare), Reverse Proxies, CMS (WordPress, Shopify, Joomla, Drupal, Wix, Squarespace, Webflow), and Frontend Frameworks.
    *   Extracts exact version numbers from observed asset signatures without guessing.
*   **Phase 3: Calibrated Bug Bounty Posture**:
    *   Clean targets with only minor defense-in-depth suggestions (missing optional headers) are rated as **`99% Secure (Well-Defended Baseline)`**.
    *   Minor issues are separated into **Unrated Security Hardening Notes** (zero severity badges, zero alarmist labels).
    *   Only true substantive risks (e.g. exposed credentials, leaked `.git`, unauthenticated endpoints) appear under **Verified Vulnerability Findings**.

### Engine 3: Static File Security & Integrity Inspection
*   **Cryptographic Multi-Hashing**: Computes SHA-256, SHA-1, and MD5 hashes via streaming chunks to handle files up to 50MB with bounded memory.
*   **PDF Document Analysis**: Passively inspects structural PDF object streams for `/JavaScript`, `/JS`, `/Launch`, and suspicious embedded streams using `pypdf`.
*   **Office Document Macro Audit**: Evaluates Microsoft Office ZIP package relationships (`word/_rels`, `xl/_rels`) for embedded VBA macros and external remote template injections.
*   **Archive Security (`.zip`)**:
    *   Zip Bomb Protection: Detects uncompressed-to-compressed compression ratios exceeding 100:1.
    *   Zip Slip / Path Traversal: Flags filenames containing directory traversal sequences (`../`, `..\`).
    *   Executable Detection: Flags hidden `.exe`, `.bat`, `.cmd`, `.sh`, `.vbs`, `.ps1` files inside archives.
*   **Image Static Inspection**: Validates dimension bounds, color space, aspect ratio, and metadata using `Pillow`.
*   **24-Hour Cryptographic Shredder**: Automatically overwrites uploaded file bytes with pseudorandom data before unlinking from disk storage.

---

## 6. Live Production Endpoints

| Resource | Environment | Live URL |
| :--- | :--- | :--- |
| **Frontend Application** | Production (Vercel) | [https://scanner-ywmt.vercel.app](https://scanner-ywmt.vercel.app) |
| **Backend API Gateway** | Production (Render) | [https://scanner-mtxg.onrender.com](https://scanner-mtxg.onrender.com) |
| **OpenAPI / Swagger Docs** | Production (Render) | [https://scanner-mtxg.onrender.com/docs](https://scanner-mtxg.onrender.com/docs) |
| **Health Check Endpoint** | Production (Render) | [https://scanner-mtxg.onrender.com/health](https://scanner-mtxg.onrender.com/health) |
| **GitHub Repository** | Public Source Control | [https://github.com/jimmy07b/Scanner](https://github.com/jimmy07b/Scanner) |

---

## 7. Verification & Quality Standards

- **Unit & Integration Tests**: 17 tests passed in 10.26s (`python -m pytest tests -v`).
- **End-to-End Suite**: All 5 verification stages passed (`python test_all_engines_e2e.py`).
- **TypeScript Compilation**: Zero compilation or lint errors on production build (`npm run build`).
- **CORS Configuration**: Automated origin regex validation (`^https://.*\.vercel\.app$`) ensuring seamless communication between Vercel and Render.
