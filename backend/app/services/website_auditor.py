import re
import time
import ssl
import socket
import datetime
import asyncio
import urllib.parse
from typing import Dict, Any, List, Tuple, Optional
import httpx
from bs4 import BeautifulSoup
import tldextract
import dns.resolver

from app.services.risk_engine import risk_engine
from app.services.report_builder import report_builder
from app.services.cms_fingerprinter import cms_fingerprinter

class WebsiteAuditor:
    """
    Engine 2: Professional Website Security Assessment & Reconnaissance Engine.
    
    Executes a strict 4-step workflow:
    1. Phase 1: Full Passive Reconnaissance (DNS, TLS, Headers, Cookies, WAF, CMS, Routes, Forms, Caching, 404)
    2. Phase 2: Bounded Active Recon (HEAD/OPTIONS, public files, login presence, response variation)
    3. Phase 3: Security Verification Checks (OWASP Top 10, headers, cookies, CORS, mixed content, safe SQLi indicators)
    4. Phase 4: Deterministic Assessment Report Generation
    """

    SENSITIVE_ROBOTS_KEYWORDS = [
        "/admin", "/wp-admin", "/backup", "/secret", "/database", "/.git", "/config", "/staging", "/api/internal", "/private"
    ]

    DATABASE_ERROR_PATTERNS = [
        r"SQL syntax.*?MySQL",
        r"Warning.*?mysql_",
        r"valid MySQL result",
        r"MySqlClient\.",
        r"PostgreSQL.*?ERROR",
        r"Warning.*?pg_",
        r"valid PostgreSQL result",
        r"Npgsql\.",
        r"Driver.*?SQL[\-\_\ ]*Server",
        r"OLE DB.*?SQL Server",
        r"SQLServer JDBC Driver",
        r"Microsoft SQL Native Client",
        r"ORA-[0-9]{4,5}",
        r"Oracle error",
        r"Oracle.*?Driver",
        r"SQLite/JDBCDriver",
        r"SQLite\.Exception",
        r"System\.Data\.SQLite\.SQLiteException",
        r"Unclosed quotation mark after the character string",
        r"quoted string not properly terminated",
        r"syntax error at or near",
        r"Dynamic SQL Error"
    ]

    async def audit_website(self, raw_url: str) -> Tuple[int, str, str, str, List[dict], List[str], dict]:
        """
        Executes the complete 4-step security assessment workflow.
        Returns: (risk_score, status, verdict, summary, findings, passed_checks, collected_data)
        """
        url = self._normalize_url(raw_url)
        parsed = urllib.parse.urlsplit(url)
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
        hostname = parsed.hostname or domain
        origin = f"{parsed.scheme}://{parsed.netloc}"

        findings: List[dict] = []
        passed_checks: List[str] = []
        is_unreachable = False

        # =========================================================================
        # PHASE 1: FULL PASSIVE RECONNAISSANCE
        # =========================================================================
        recon_data: Dict[str, Any] = {
            "target_url": url,
            "domain": domain,
            "hostname": hostname,
            "origin": origin,
            "scheme": parsed.scheme,
            "host": parsed.netloc,
            "status_code": None,
            "response_time_ms": None,
            "final_url": url,
            "redirect_chain": [],
            "response_headers": {},
            "cookies": [],
            "dns": {},
            "tls": {},
            "waf_and_cdn": {},
            "server_and_proxy": {},
            "cms_details": {},
            "technology_profile": {},
            "metadata": {},
            "forms": [],
            "client_assets": {},
            "discovered_routes": [],
            "robots_txt": {},
            "sitemap_xml": {},
            "security_txt": {},
            "well_known": {},
            "error_page_fingerprint": {},
            "caching": {},
        }

        # 1.1 DNS & Domain Signals
        dns_data = await asyncio.to_thread(self._passive_dns_recon, domain)
        recon_data["dns"] = dns_data
        recon_data["dns_recon"] = dns_data

        # 1.2 TLS Handshake & Certificate Details
        if parsed.scheme == "https" or not parsed.scheme:
            tls_data = await asyncio.to_thread(self._passive_tls_recon, hostname)
            recon_data["tls"] = tls_data
            recon_data["tls_telemetry"] = tls_data

        # 1.3 HTTP Network Fetch & Passive Transport Observation
        start_time = time.time()
        root_html = ""
        root_resp: Optional[httpx.Response] = None

        try:
            async with httpx.AsyncClient(
                timeout=12.0,
                follow_redirects=True,
                verify=False,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RootLayer-SecurityAuditor/1.0"
                }
            ) as client:
                resp = await client.get(url)
                root_resp = resp
                duration_ms = int((time.time() - start_time) * 1000)
                recon_data["response_time_ms"] = duration_ms
                recon_data["status_code"] = resp.status_code
                recon_data["final_url"] = str(resp.url)
                recon_data["redirect_chain"] = [str(r.url) for r in resp.history] + [str(resp.url)]

                headers_lower = {k.lower(): v for k, v in resp.headers.items()}
                recon_data["response_headers"] = dict(resp.headers)
                recon_data["cross_origin_headers"] = {
                    "coop": headers_lower.get("cross-origin-opener-policy"),
                    "coep": headers_lower.get("cross-origin-embedder-policy"),
                    "corp": headers_lower.get("cross-origin-resource-policy")
                }

                # 1.4 Cookie Flags & Scope
                recon_data["cookies"] = self._parse_cookies(resp)

                # 1.5 Server & Proxy Fingerprints
                recon_data["server_and_proxy"] = self._fingerprint_server_and_proxy(headers_lower)

                # 1.6 CDN / WAF Detection
                recon_data["waf_and_cdn"] = self._detect_waf_and_cdn(headers_lower, resp.cookies)

                # 1.7 Content-Type & Caching Behavior
                recon_data["caching"] = {
                    "content_type": headers_lower.get("content-type", "Not specified"),
                    "cache_control": headers_lower.get("cache-control", "Not set"),
                    "pragma": headers_lower.get("pragma", "Not set"),
                    "expires": headers_lower.get("expires", "Not set"),
                    "etag": headers_lower.get("etag", "Not set"),
                    "last_modified": headers_lower.get("last-modified", "Not set"),
                    "age": headers_lower.get("age", "Not set")
                }

                # 1.8 HTML Document & Metadata Analysis
                ct = headers_lower.get("content-type", "")
                if "text/html" in ct:
                    root_html = resp.text
                    soup = BeautifulSoup(root_html[:400000], "html.parser")
                    recon_data["metadata"] = self._extract_metadata(soup)
                    recon_data["forms"] = self._extract_forms(soup)
                    recon_data["client_assets"] = self._extract_assets(soup, domain)
                    recon_data["discovered_routes"] = self._extract_discovered_routes(soup, domain)

                # 1.9 robots.txt & sitemap.xml
                recon_data["robots_txt"] = await self._probe_robots_txt(client, origin)
                recon_data["sitemap_xml"] = await self._probe_sitemap_xml(client, origin)

                # 1.10 security.txt & .well-known probes
                recon_data["security_txt"] = await self._probe_security_txt(client, origin)
                recon_data["well_known"] = await self._probe_well_known(client, origin)

                # 1.11 Error Page Fingerprint (Passive inspection of non-existent probe)
                recon_data["error_page_fingerprint"] = await self._probe_error_page(client, origin)

                # 1.12 CMS & Technology Stack Fingerprinting
                cms_details, cms_findings, cms_passed = await cms_fingerprinter.inspect_cms(
                    html_text=root_html,
                    response_headers=dict(resp.headers),
                    client=client,
                    origin=origin
                )
                recon_data["cms_details"] = cms_details
                recon_data["technology_profile"] = cms_details.get("technology_profile", {})

                # =========================================================================
                # PHASE 2: BOUNDED ACTIVE RECONNAISSANCE (Low-rate, Safe, Authorized)
                # =========================================================================
                active_recon_results = await self._run_bounded_active_recon(
                    client=client,
                    origin=origin,
                    domain=domain,
                    root_resp=root_resp,
                    discovered_forms=recon_data["forms"],
                    discovered_routes=recon_data["discovered_routes"]
                )
                recon_data["active_recon"] = active_recon_results

        except httpx.RequestError as e:
            is_unreachable = True
            findings.append({
                "id": "SEC-NET-UNREACHABLE",
                "finding_key": "connectivity.request_error",
                "title": "Target Host Unreachable",
                "severity": "critical",
                "confidence": "high",
                "category": "Connectivity & Availability",
                "evidence": f"Failed to establish network connection with '{url}': {str(e)[:180]}",
                "recommendation": "Verify target DNS records, network firewalls, and server availability."
            })

        # =========================================================================
        # PHASE 3: DETERMINISTIC SECURITY VERIFICATION CHECKS (OWASP Top 10 Style)
        # =========================================================================
        if not is_unreachable:
            sec_findings, sec_passed = self._run_security_checks(recon_data)
            findings.extend(sec_findings)
            passed_checks.extend(sec_passed)

        # =========================================================================
        # PHASE 4: DETERMINISTIC REPORT GENERATION & SCORING
        # =========================================================================
        risk_score = risk_engine.compute_score(findings)
        status_label = risk_engine.classify_status(risk_score)
        verdict = "unreachable / broken" if is_unreachable else status_label

        summary = report_builder.build_summary(
            findings=findings,
            passed_count=len(passed_checks),
            target_name=domain,
            verdict=verdict
        )

        return risk_score, status_label, verdict, summary, findings, passed_checks, recon_data

    # =========================================================================
    # RECON MODULE: Passive DNS & Domain Signals
    # =========================================================================
    def _passive_dns_recon(self, domain: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "dmarc": None,
            "dmarc_policy": None,
            "spf": None,
            "spf_mechanisms": [],
            "caa": [],
            "mx": [],
            "dnssec": False,
            "a_records": []
        }
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2.5
        resolver.timeout = 2.0

        # DMARC
        try:
            dmarc_txts = [t.to_text().strip('"') for t in resolver.resolve(f"_dmarc.{domain}", "TXT")]
            dmarc_rec = next((r for r in dmarc_txts if r.lower().startswith("v=dmarc1")), None)
            if dmarc_rec:
                data["dmarc"] = dmarc_rec
                p_match = re.search(r"\bp=([a-zA-Z]+)", dmarc_rec, re.IGNORECASE)
                data["dmarc_policy"] = p_match.group(1).lower() if p_match else "unspecified"
        except Exception:
            pass

        # SPF
        try:
            txts = [t.to_text().strip('"') for t in resolver.resolve(domain, "TXT")]
            spf_rec = next((r for r in txts if r.lower().startswith("v=spf1")), None)
            if spf_rec:
                data["spf"] = spf_rec
                data["spf_mechanisms"] = spf_rec.split()
        except Exception:
            pass

        # CAA
        try:
            caas = [t.to_text().strip('"') for t in resolver.resolve(domain, "CAA")]
            data["caa"] = caas
        except Exception:
            pass

        # MX
        try:
            mxs = [f"{t.preference} {t.exchange.to_text().rstrip('.')}" for t in resolver.resolve(domain, "MX")]
            data["mx"] = mxs
        except Exception:
            pass

        # DNSSEC check
        try:
            dnskeys = resolver.resolve(domain, "DNSKEY")
            data["dnssec"] = bool(dnskeys)
        except Exception:
            pass

        # A Records
        try:
            a_recs = [t.to_text() for t in resolver.resolve(domain, "A")]
            data["a_records"] = a_recs[:5]
        except Exception:
            pass

        return data

    # =========================================================================
    # RECON MODULE: Passive TLS Handshake & Certificate Details
    # =========================================================================
    def _passive_tls_recon(self, hostname: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "inspected": False,
            "protocol": None,
            "cipher": None,
            "issuer": None,
            "subject": None,
            "valid_from": None,
            "valid_to": None,
            "days_remaining": None,
            "sans": [],
            "self_signed": False
        }
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=hostname) as s:
                s.settimeout(3.5)
                s.connect((hostname, 443))
                cert = s.getpeercert()
                version = s.version()
                cipher = s.cipher()

                data["inspected"] = True
                data["protocol"] = version
                data["cipher"] = cipher[0] if cipher else None

                issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                data["issuer"] = issuer_dict.get("organizationName") or issuer_dict.get("commonName") or "Unknown Issuer"

                subj_dict = dict(x[0] for x in cert.get("subject", []))
                data["subject"] = subj_dict.get("commonName") or "Unknown Subject"

                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")
                data["valid_from"] = not_before
                data["valid_to"] = not_after

                if not_after:
                    dt = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                    data["days_remaining"] = (dt - now).days

                sans = [val for (typ, val) in cert.get("subjectAltName", []) if typ == "DNS"]
                data["sans"] = sans[:15]
        except Exception:
            data["inspected"] = False
        return data

    # =========================================================================
    # RECON MODULE: Cookie Flags and Scope
    # =========================================================================
    def _parse_cookies(self, resp: httpx.Response) -> List[Dict[str, Any]]:
        cookies = []
        for sc in resp.headers.get_list("set-cookie"):
            parts = [p.strip() for p in sc.split(";")]
            if not parts or not parts[0]:
                continue
            name_val = parts[0].split("=", 1)
            c_name = name_val[0].strip()

            has_secure = any(p.lower() == "secure" for p in parts)
            has_httponly = any(p.lower() == "httponly" for p in parts)
            samesite = "Not set"
            domain = "Host"
            path = "/"

            for p in parts[1:]:
                pl = p.lower()
                if pl.startswith("samesite="):
                    samesite = p.split("=", 1)[1].strip()
                elif pl.startswith("domain="):
                    domain = p.split("=", 1)[1].strip()
                elif pl.startswith("path="):
                    path = p.split("=", 1)[1].strip()

            cookies.append({
                "name": c_name,
                "secure": has_secure,
                "httponly": has_httponly,
                "samesite": samesite,
                "domain": domain,
                "path": path,
                "has_secure_prefix": c_name.startswith("__Secure-") or c_name.startswith("__Host-")
            })
        return cookies

    # =========================================================================
    # RECON MODULE: Server, Proxy & WAF/CDN Fingerprints
    # =========================================================================
    def _fingerprint_server_and_proxy(self, headers: Dict[str, str]) -> Dict[str, Any]:
        return {
            "server_header": headers.get("server", "Not disclosed"),
            "powered_by": headers.get("x-powered-by", "Not disclosed"),
            "via": headers.get("via", "Not present"),
            "x_cache": headers.get("x-cache", "Not present"),
            "x_served_by": headers.get("x-served-by", "Not present"),
            "proxy_agent": headers.get("x-proxy-agent", "Not present")
        }

    def _detect_waf_and_cdn(self, headers: Dict[str, str], cookies: Any) -> Dict[str, Any]:
        signatures = []
        server = headers.get("server", "").lower()

        if "cloudflare" in server or "cf-ray" in headers or "__cf_bm" in str(cookies):
            signatures.append("Cloudflare (CDN / Cloud Shield)")
        if "cloudfront" in server or "x-amz-cf-id" in headers:
            signatures.append("Amazon CloudFront (CDN)")
        if "fastly" in server or "x-served-by" in headers and "cache-" in headers["x-served-by"]:
            signatures.append("Fastly (Edge Cloud)")
        if "akamaighost" in server or "x-akamai-transformed" in headers:
            signatures.append("Akamai (Edge CDN / WAF)")
        if "sucuri" in server or "x-sucuri-id" in headers:
            signatures.append("Sucuri (Cloud WAF)")
        if "x-iinfo" in headers or "incap_ses" in str(cookies):
            signatures.append("Imperva Incapsula (WAF)")
        if "awswaf" in str(headers):
            signatures.append("AWS WAF")
        if "x-azure-ref" in headers:
            signatures.append("Azure Front Door (CDN / WAF)")

        return {
            "detected": len(signatures) > 0,
            "provider": ", ".join(signatures) if signatures else "None detected",
            "signatures_observed": signatures
        }

    # =========================================================================
    # RECON MODULE: HTML Metadata, Forms, Assets & Discovered Routes
    # =========================================================================
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        title = soup.find("title")
        title_text = title.string.strip()[:140] if title and title.string else "None detected"

        desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        desc_text = desc.get("content", "").strip()[:200] if desc else "None"

        canonical = soup.find("link", attrs={"rel": "canonical"})
        canonical_url = canonical.get("href", "").strip() if canonical else "None declared"

        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_image = soup.find("meta", attrs={"property": "og:image"})

        return {
            "title": title_text,
            "description": desc_text,
            "canonical_url": canonical_url,
            "open_graph_present": bool(og_title or og_image),
            "og_title": og_title.get("content") if og_title else None
        }

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        forms_list = []
        for f in soup.find_all("form"):
            action = f.get("action", "") or "[Self]"
            method = (f.get("method") or "GET").upper()
            inputs = f.find_all(["input", "textarea", "select"])
            has_password = any((i.get("type") or "").lower() == "password" for i in inputs)
            has_csrf = any("csrf" in (i.get("name") or "").lower() or "token" in (i.get("name") or "").lower() for i in inputs)
            forms_list.append({
                "action": action,
                "method": method,
                "inputs_count": len(inputs),
                "has_password": has_password,
                "has_csrf": has_csrf
            })
        return forms_list

    def _extract_assets(self, soup: BeautifulSoup, target_domain: str) -> Dict[str, Any]:
        scripts = []
        third_party_scripts = []
        missing_sri = []

        for s in soup.find_all("script", src=True):
            src = s.get("src", "").strip()
            if not src:
                continue
            scripts.append(src)
            is_external = False
            if src.startswith("http://") or src.startswith("https://") or src.startswith("//"):
                ext = tldextract.extract(src)
                s_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
                if s_domain.lower() != target_domain.lower():
                    is_external = True

            if is_external:
                third_party_scripts.append(src)
                if not s.get("integrity"):
                    missing_sri.append(src)

        stylesheets = [link.get("href") for link in soup.find_all("link", rel="stylesheet") if link.get("href")]
        return {
            "total_scripts": len(scripts),
            "third_party_scripts": len(third_party_scripts),
            "missing_sri_count": len(missing_sri),
            "missing_sri_samples": missing_sri[:5],
            "total_stylesheets": len(stylesheets)
        }

    def _extract_discovered_routes(self, soup: BeautifulSoup, domain: str) -> List[str]:
        routes = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if href.startswith("/"):
                path = href.split("?")[0].split("#")[0]
                if len(path) > 1 and len(path) < 60:
                    routes.add(path)
            elif domain in href:
                parsed = urllib.parse.urlsplit(href)
                if parsed.path and len(parsed.path) < 60:
                    routes.add(parsed.path)
        return sorted(list(routes))[:20]

    # =========================================================================
    # RECON PROBES: robots.txt, sitemap.xml, security.txt, .well-known & Error Page
    # =========================================================================
    async def _probe_robots_txt(self, client: httpx.AsyncClient, origin: str) -> Dict[str, Any]:
        url = f"{origin}/robots.txt"
        try:
            res = await client.get(url, timeout=3.5)
            if res.status_code == 200:
                lines = res.text.splitlines()
                disallowed = []
                for line in lines:
                    if line.lower().startswith("disallow:"):
                        p = line.split(":", 1)[1].strip()
                        if any(k in p.lower() for k in self.SENSITIVE_ROBOTS_KEYWORDS):
                            disallowed.append(p)
                return {
                    "accessible": True,
                    "url": url,
                    "rules_count": len(lines),
                    "sensitive_disallowed_paths": disallowed[:10]
                }
        except Exception:
            pass
        return {"accessible": False, "url": url, "rules_count": 0, "sensitive_disallowed_paths": []}

    async def _probe_sitemap_xml(self, client: httpx.AsyncClient, origin: str) -> Dict[str, Any]:
        url = f"{origin}/sitemap.xml"
        try:
            res = await client.get(url, timeout=3.5)
            if res.status_code == 200 and ("xml" in res.headers.get("content-type", "") or "<url" in res.text or "<sitemap" in res.text):
                return {"accessible": True, "url": url}
        except Exception:
            pass
        return {"accessible": False, "url": url}

    async def _probe_security_txt(self, client: httpx.AsyncClient, origin: str) -> Dict[str, Any]:
        for p in [f"{origin}/.well-known/security.txt", f"{origin}/security.txt"]:
            try:
                res = await client.get(p, timeout=3.5)
                if res.status_code == 200 and "contact:" in res.text.lower():
                    c_match = re.search(r"^contact:\s*(.+)$", res.text, re.MULTILINE | re.IGNORECASE)
                    e_match = re.search(r"^expires:\s*(.+)$", res.text, re.MULTILINE | re.IGNORECASE)
                    return {
                        "accessible": True,
                        "url": p,
                        "contact": c_match.group(1).strip() if c_match else None,
                        "expires": e_match.group(1).strip() if e_match else None
                    }
            except Exception:
                pass
        return {"accessible": False, "url": None, "contact": None, "expires": None}

    async def _probe_well_known(self, client: httpx.AsyncClient, origin: str) -> Dict[str, Any]:
        endpoints = {
            "change_password": f"{origin}/.well-known/change-password",
            "openid_configuration": f"{origin}/.well-known/openid-configuration",
            "assetlinks": f"{origin}/.well-known/assetlinks.json"
        }
        discovered = {}
        for k, ep in endpoints.items():
            try:
                res = await client.get(ep, timeout=2.5)
                if res.status_code in [200, 301, 302]:
                    discovered[k] = {"status": res.status_code, "accessible": True}
                else:
                    discovered[k] = {"status": res.status_code, "accessible": False}
            except Exception:
                discovered[k] = {"status": "unreachable", "accessible": False}
        return discovered

    async def _probe_error_page(self, client: httpx.AsyncClient, origin: str) -> Dict[str, Any]:
        probe_url = f"{origin}/.rootlayer-recon-probe-404-check"
        try:
            res = await client.get(probe_url, timeout=3.5)
            # Check for stack trace or detailed server leak
            leaks_stack = any(s in res.text.lower() for s in ["traceback", "stack trace", "exception in thread", "fatal error in"])
            discloses_version = bool(re.search(r"(Apache|nginx|IIS|LiteSpeed)/\d+\.\d+", res.text, re.IGNORECASE))
            return {
                "status_code": res.status_code,
                "is_custom_404": res.status_code == 404 and len(res.text) > 200,
                "leaks_stack_trace": leaks_stack,
                "discloses_server_version": discloses_version
            }
        except Exception:
            return {"status_code": None, "is_custom_404": False, "leaks_stack_trace": False, "discloses_server_version": False}

    # =========================================================================
    # PHASE 2: BOUNDED ACTIVE RECONNAISSANCE (Safe, Low-Noise, Rate-Limited)
    # =========================================================================
    async def _run_bounded_active_recon(
        self,
        client: httpx.AsyncClient,
        origin: str,
        domain: str,
        root_resp: Optional[httpx.Response],
        discovered_forms: List[Dict[str, Any]],
        discovered_routes: List[str]
    ) -> Dict[str, Any]:
        active_results: Dict[str, Any] = {
            "allowed_methods": [],
            "trace_method_enabled": False,
            "sensitive_files": {},
            "login_paths_status": {},
            "http_redirect_enforced": False,
            "response_variation_consistent": True
        }

        # 1. OPTIONS request to inspect allowed HTTP methods
        try:
            opt_res = await client.options(origin, timeout=3.5)
            allow_hdr = opt_res.headers.get("allow", "")
            if allow_hdr:
                methods = [m.strip().upper() for m in allow_hdr.split(",")]
                active_results["allowed_methods"] = methods
                active_results["trace_method_enabled"] = "TRACE" in methods
        except Exception:
            pass

        # 2. Bounded public file presence checks (max 3 safe requests)
        files_to_check = {
            "env": f"{origin}/.env",
            "git_head": f"{origin}/.git/HEAD",
            "crossdomain": f"{origin}/crossdomain.xml"
        }
        for name, file_url in files_to_check.items():
            try:
                res = await client.get(file_url, timeout=3.0)
                ct = res.headers.get("content-type", "").lower()
                if res.status_code == 200 and "text/html" not in ct:
                    if name == "env" and "=" in res.text and any(k in res.text for k in ["DB_", "APP_", "KEY", "SECRET"]):
                        active_results["sensitive_files"][name] = {"exposed": True, "url": file_url}
                    elif name == "git_head" and res.text.strip().startswith("ref: refs/"):
                        active_results["sensitive_files"][name] = {"exposed": True, "url": file_url}
                    elif name == "crossdomain" and "<cross-domain-policy>" in res.text:
                        active_results["sensitive_files"][name] = {"exposed": True, "url": file_url}
                    else:
                        active_results["sensitive_files"][name] = {"exposed": False}
                else:
                    active_results["sensitive_files"][name] = {"exposed": False}
            except Exception:
                active_results["sensitive_files"][name] = {"exposed": False}

        # 3. Known authentication surface status (bounded to 2 HEAD checks)
        paths_to_probe = ["/login", "/admin"]
        for p in paths_to_probe:
            try:
                h_res = await client.head(f"{origin}{p}", timeout=3.0)
                active_results["login_paths_status"][p] = h_res.status_code
            except Exception:
                pass

        # 4. Safe plain HTTP to HTTPS redirection check
        try:
            plain_http = f"http://{domain}"
            plain_res = await client.get(plain_http, timeout=3.5, follow_redirects=False)
            if plain_res.status_code in [301, 302, 307, 308]:
                loc = plain_res.headers.get("location", "")
                active_results["http_redirect_enforced"] = loc.startswith("https://")
            else:
                active_results["http_redirect_enforced"] = False
        except Exception:
            pass

        # 5. Response consistency check (compare root GET status vs HEAD status)
        try:
            head_res = await client.head(origin, timeout=3.0)
            if root_resp:
                active_results["response_variation_consistent"] = (head_res.status_code == root_resp.status_code)
        except Exception:
            pass

        return active_results

    # =========================================================================
    # PHASE 3: DETERMINISTIC SECURITY CHECKS (OWASP Top 10 + Web Posture)
    # =========================================================================
    def _run_security_checks(self, recon: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        findings: List[Dict[str, Any]] = []
        passed: List[str] = []

        headers = recon.get("response_headers", {})
        headers_lower = {k.lower(): str(v) for k, v in headers.items()}
        final_url = recon.get("final_url", "")
        final_is_https = final_url.startswith("https://")
        domain = recon.get("domain", "")

        # -------------------------------------------------------------
        # OWASP A02: Cryptographic Failures & Transport
        # -------------------------------------------------------------
        # Transport HTTPS
        if not final_is_https:
            findings.append({
                "id": "SEC-CRYPTO-HTTP-INSECURE",
                "finding_key": "tls.https.missing",
                "title": "Plain HTTP Transport In Use (Missing HTTPS)",
                "severity": "critical",
                "confidence": "high",
                "category": "A02: Cryptographic Failures",
                "evidence": f"Target was resolved to unencrypted HTTP ({final_url}). Data in transit is subject to eavesdropping and MITM manipulation.",
                "recommendation": "Deploy a valid TLS certificate and enforce automatic HTTP 301 redirects to HTTPS."
            })
        else:
            passed.append("HTTPS transport active and verified on final destination")

        # HSTS
        if final_is_https:
            hsts = headers_lower.get("strict-transport-security")
            if not hsts:
                findings.append({
                    "id": "SEC-HDR-HSTS-MISSING",
                    "finding_key": "http.headers.hsts.missing",
                    "title": "Strict-Transport-Security (HSTS) Header Missing",
                    "severity": "high",
                    "confidence": "high",
                    "category": "A02: Cryptographic Failures",
                    "evidence": f"Origin serves HTTPS but omitted the 'Strict-Transport-Security' response header.",
                    "recommendation": "Add header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
                })
            else:
                m = re.search(r"max-age=(\d+)", hsts)
                if m and int(m.group(1)) < 10368000:
                    findings.append({
                        "id": "SEC-HDR-HSTS-SHORT",
                        "finding_key": "http.headers.hsts.short_duration",
                        "title": "HSTS max-age Duration Too Short",
                        "severity": "low",
                        "confidence": "high",
                        "category": "A02: Cryptographic Failures",
                        "evidence": f"Observed HSTS header '{hsts}' defines max-age={m.group(1)}s (minimum recommended: 31,536,000s).",
                        "recommendation": "Increase HSTS max-age to at least 31536000 (1 year)."
                    })
                else:
                    passed.append(f"Strict-Transport-Security (HSTS) enforced ({hsts})")

        # TLS Telemetry
        tls = recon.get("tls", {})
        if tls.get("inspected"):
            days = tls.get("days_remaining")
            proto = tls.get("protocol")
            if days is not None:
                if days < 0:
                    findings.append({
                        "id": "SEC-CRYPTO-TLS-EXPIRED",
                        "finding_key": "tls.cert.expired",
                        "title": "SSL/TLS Certificate Expired",
                        "severity": "critical",
                        "confidence": "high",
                        "category": "A02: Cryptographic Failures",
                        "evidence": f"Certificate expired on '{tls.get('valid_to')}' ({abs(days)} day(s) ago).",
                        "recommendation": "Renew and replace the expired TLS certificate immediately."
                    })
                elif days <= 14:
                    findings.append({
                        "id": "SEC-CRYPTO-TLS-EXPIRING",
                        "finding_key": "tls.cert.expiring_soon",
                        "title": f"SSL/TLS Certificate Expiring Soon ({days} Days Remaining)",
                        "severity": "high",
                        "confidence": "high",
                        "category": "A02: Cryptographic Failures",
                        "evidence": f"Certificate expires on '{tls.get('valid_to')}' (in {days} day(s)).",
                        "recommendation": "Automate certificate renewal before the current certificate lapses."
                    })
                else:
                    passed.append(f"TLS certificate valid for {days} days (Expires {tls.get('valid_to')})")

            if proto in ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]:
                findings.append({
                    "id": "SEC-CRYPTO-TLS-DEPRECATED",
                    "finding_key": "tls.protocol.deprecated",
                    "title": f"Deprecated TLS Protocol ({proto}) Negotiated",
                    "severity": "high",
                    "confidence": "high",
                    "category": "A02: Cryptographic Failures",
                    "evidence": f"Server negotiated protocol '{proto}', which is deprecated by RFC 8996.",
                    "recommendation": "Disable TLS 1.0 and 1.1; enforce TLS 1.2 and TLS 1.3 exclusively."
                })
            elif proto in ["TLSv1.2", "TLSv1.3"]:
                passed.append(f"Modern TLS protocol enforced ({proto}, {tls.get('cipher')})")

        # -------------------------------------------------------------
        # OWASP A05: Security Misconfiguration (Headers & Policies)
        # -------------------------------------------------------------
        # CSP
        csp = headers_lower.get("content-security-policy")
        if not csp:
            findings.append({
                "id": "SEC-HDR-CSP-MISSING",
                "finding_key": "http.headers.csp.missing",
                "title": "Content-Security-Policy (CSP) Missing",
                "severity": "medium",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "No 'Content-Security-Policy' or 'Content-Security-Policy-Report-Only' header returned.",
                "recommendation": "Define a Content-Security-Policy (e.g. default-src 'self') to mitigate XSS attacks."
            })
        else:
            if "'unsafe-inline'" in csp and "script-src" in csp:
                findings.append({
                    "id": "SEC-HDR-CSP-UNSAFE-INLINE",
                    "finding_key": "http.headers.csp.unsafe_inline",
                    "title": "Content-Security-Policy Permits 'unsafe-inline' Scripts",
                    "severity": "low",
                    "confidence": "high",
                    "category": "A05: Security Misconfiguration",
                    "evidence": f"Content-Security-Policy contains 'unsafe-inline': {csp[:130]}...",
                    "recommendation": "Migrate inline script blocks to cryptographic nonces or hashes."
                })
            else:
                passed.append("Content-Security-Policy (CSP) active and configured")

        # X-Frame-Options
        xfo = headers_lower.get("x-frame-options")
        has_frame_ancestors = csp and "frame-ancestors" in csp
        if not xfo and not has_frame_ancestors:
            findings.append({
                "id": "SEC-HDR-XFO-MISSING",
                "finding_key": "http.headers.x_frame_options.missing",
                "title": "Clickjacking Protection Missing (X-Frame-Options)",
                "severity": "medium",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "Neither 'X-Frame-Options' header nor CSP 'frame-ancestors' directive was detected.",
                "recommendation": "Set 'X-Frame-Options: SAMEORIGIN' or add 'frame-ancestors 'self'' to CSP."
            })
        elif xfo:
            passed.append(f"Clickjacking defense enforced ({xfo})")

        # X-Content-Type-Options
        xcto = headers_lower.get("x-content-type-options")
        if not xcto or "nosniff" not in xcto.lower():
            findings.append({
                "id": "SEC-HDR-NOSNIFF-MISSING",
                "finding_key": "http.headers.x_content_type_options.missing",
                "title": "Missing X-Content-Type-Options Header",
                "severity": "low",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "Header 'X-Content-Type-Options: nosniff' was not returned.",
                "recommendation": "Add header: X-Content-Type-Options: nosniff"
            })
        else:
            passed.append("MIME-type sniffing protection active (nosniff)")

        # Referrer-Policy
        ref_pol = headers_lower.get("referrer-policy")
        if not ref_pol:
            findings.append({
                "id": "SEC-HDR-REFERRER-MISSING",
                "finding_key": "http.headers.referrer_policy.missing",
                "title": "Missing Referrer-Policy Header",
                "severity": "low",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "No 'Referrer-Policy' header was declared on root response.",
                "recommendation": "Add: Referrer-Policy: strict-origin-when-cross-origin"
            })
        else:
            passed.append(f"Referrer-Policy active ({ref_pol})")

        # Modern Cross-Origin Isolation Headers (COOP, COEP, CORP)
        coop = headers_lower.get("cross-origin-opener-policy")
        if not coop:
            findings.append({
                "id": "SEC-HDR-COOP-MISSING",
                "finding_key": "http.headers.coop.missing",
                "title": "Cross-Origin-Opener-Policy (COOP) Missing",
                "severity": "low",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "Response did not declare 'Cross-Origin-Opener-Policy'. Window opener references remain exposed across origins.",
                "recommendation": "Add: Cross-Origin-Opener-Policy: same-origin"
            })
        else:
            passed.append(f"Cross-Origin-Opener-Policy (COOP) active ({coop})")

        # CORS Misconfiguration
        cors_origin = headers_lower.get("access-control-allow-origin")
        cors_cred = headers_lower.get("access-control-allow-credentials")
        if cors_origin == "*" and cors_cred == "true":
            findings.append({
                "id": "SEC-CORS-WILDCARD-CRED",
                "finding_key": "cors.wildcard_with_credentials",
                "title": "Insecure CORS: Wildcard Origin With Credentials",
                "severity": "high",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "Server declared 'Access-Control-Allow-Origin: *' in conjunction with 'Access-Control-Allow-Credentials: true'.",
                "recommendation": "Specify explicit trusted origins instead of wildcard '*' when credentials are supported."
            })

        # DNS Posture: DMARC & SPF
        dns_data = recon.get("dns", {})
        dmarc = dns_data.get("dmarc")
        dmarc_pol = dns_data.get("dmarc_policy")
        if not dmarc:
            findings.append({
                "id": "SEC-DNS-DMARC-MISSING",
                "finding_key": "dns.dmarc.missing",
                "title": "DMARC Spoofing Protection Record Missing",
                "severity": "medium",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": f"No TXT record found at '_dmarc.{domain}'. Domain is vulnerable to direct sender email spoofing.",
                "recommendation": "Publish a DMARC record at '_dmarc.{domain}' (e.g. 'v=DMARC1; p=quarantine;')."
            })
        elif dmarc_pol == "none":
            findings.append({
                "id": "SEC-DNS-DMARC-NONE",
                "finding_key": "dns.dmarc.policy_none",
                "title": "DMARC Policy in Inactive Monitoring Mode (p=none)",
                "severity": "low",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": f"DMARC record at '_dmarc.{domain}' specifies 'p=none', which does not block unauthorized sender spoofing.",
                "recommendation": "Upgrade DMARC policy from 'p=none' to 'p=quarantine' or 'p=reject'."
            })
        else:
            passed.append(f"DMARC email protection enforced (p={dmarc_pol})")

        spf = dns_data.get("spf")
        if not spf:
            findings.append({
                "id": "SEC-DNS-SPF-MISSING",
                "finding_key": "dns.spf.missing",
                "title": "Sender Policy Framework (SPF) Record Missing",
                "severity": "low",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": f"No TXT record beginning with 'v=spf1' was found on '{domain}'.",
                "recommendation": "Publish an SPF record designating authorized email sending servers."
            })
        elif "+all" in spf:
            findings.append({
                "id": "SEC-DNS-SPF-PERMISSIVE",
                "finding_key": "dns.spf.permissive",
                "title": "Overly Permissive SPF Record (+all)",
                "severity": "high",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": f"Observed SPF record '{spf}' contains '+all', allowing any IP address worldwide to send mail for this domain.",
                "recommendation": "Replace '+all' with '-all' or '~all'."
            })
        else:
            passed.append("Sender Policy Framework (SPF) record active")

        # -------------------------------------------------------------
        # OWASP A06: Vulnerable and Outdated Components (Version Disclosure)
        # -------------------------------------------------------------
        srv = headers_lower.get("server", "")
        if re.search(r"/\d+(\.\d+)?", srv):
            findings.append({
                "id": "SEC-INFO-SERVER-VERSION",
                "finding_key": "info_disclosure.server_version",
                "title": "Web Server Software Version Disclosed",
                "severity": "low",
                "confidence": "high",
                "category": "A06: Vulnerable & Outdated Components",
                "evidence": f"Server banner exposes specific software version: '{srv}'.",
                "recommendation": "Suppress software version numbers in server banner configuration."
            })
        elif srv:
            passed.append(f"Server banner does not expose version numbers ({srv})")

        pby = headers_lower.get("x-powered-by", "")
        if pby and pby != "Not disclosed":
            findings.append({
                "id": "SEC-INFO-POWERED-BY",
                "finding_key": "info_disclosure.x_powered_by",
                "title": "Backend Technology Disclosed in X-Powered-By",
                "severity": "low",
                "confidence": "high",
                "category": "A06: Vulnerable & Outdated Components",
                "evidence": f"HTTP header 'X-Powered-By: {pby}' discloses underlying backend runtime.",
                "recommendation": "Disable the 'X-Powered-By' header in backend application configuration."
            })

        # -------------------------------------------------------------
        # OWASP A07: Identification and Authentication Failures (Cookies & Forms)
        # -------------------------------------------------------------
        cookies = recon.get("cookies", [])
        session_names = ["session", "token", "auth", "jwt", "sid", "connect.sid", "phpsessid", "jsessionid"]
        for c in cookies:
            c_name = c.get("name", "")
            if final_is_https and not c.get("secure"):
                findings.append({
                    "id": f"SEC-AUTH-COOKIE-SECURE-{c_name[:20]}",
                    "finding_key": f"cookies.secure.missing.{c_name}",
                    "title": f"Cookie '{c_name}' Missing Secure Attribute",
                    "severity": "medium",
                    "confidence": "high",
                    "category": "A07: Identification & Authentication",
                    "evidence": f"Set-Cookie for '{c_name}' lacks '; Secure' over HTTPS connection.",
                    "recommendation": "Enforce '; Secure' on all cookies served across HTTPS origins."
                })
            if any(s in c_name.lower() for s in session_names) and not c.get("httponly"):
                findings.append({
                    "id": f"SEC-AUTH-COOKIE-HTTPONLY-{c_name[:20]}",
                    "finding_key": f"cookies.httponly.missing.{c_name}",
                    "title": f"Authentication Cookie '{c_name}' Missing HttpOnly Flag",
                    "severity": "high",
                    "confidence": "high",
                    "category": "A07: Identification & Authentication",
                    "evidence": f"Authentication cookie '{c_name}' lacks '; HttpOnly', allowing script access via document.cookie.",
                    "recommendation": "Add '; HttpOnly' to all authentication and session tokens."
                })

        # Forms
        forms = recon.get("forms", [])
        for f in forms:
            action = f.get("action", "")
            if action.startswith("http://"):
                findings.append({
                    "id": "SEC-AUTH-FORM-HTTP-ACTION",
                    "finding_key": "forms.insecure_action",
                    "title": "HTML Form Action Targets Plain HTTP",
                    "severity": "high",
                    "confidence": "high",
                    "category": "A07: Identification & Authentication",
                    "evidence": f"HTML form specifies unencrypted submission endpoint: '{action}'.",
                    "recommendation": "Update form action to submit exclusively to HTTPS."
                })

        # -------------------------------------------------------------
        # OWASP A08: Software and Data Integrity Failures (SRI & Mixed Content)
        # -------------------------------------------------------------
        assets = recon.get("client_assets", {})
        if assets.get("missing_sri_count", 0) > 0:
            samples = assets.get("missing_sri_samples", [])
            findings.append({
                "id": "SEC-INTEGRITY-SRI-MISSING",
                "finding_key": "html.scripts.sri_missing",
                "title": "Third-Party CDN Scripts Missing Subresource Integrity (SRI)",
                "severity": "low",
                "confidence": "high",
                "category": "A08: Software & Data Integrity",
                "evidence": f"Found {assets['missing_sri_count']} third-party script(s) loaded without 'integrity' hash: {', '.join(samples[:2])}.",
                "recommendation": "Add 'integrity' (sha384/sha512) and 'crossorigin=\"anonymous\"' to external CDN script tags."
            })
        elif assets.get("total_scripts", 0) > 0:
            passed.append("Third-party CDN scripts enforce cryptographic Subresource Integrity (SRI)")

        # -------------------------------------------------------------
        # OWASP A09: Security Logging & Monitoring (security.txt)
        # -------------------------------------------------------------
        st = recon.get("security_txt", {})
        if not st.get("accessible"):
            findings.append({
                "id": "SEC-LOG-SECURITY-TXT-MISSING",
                "finding_key": "disclosure.security_txt.missing",
                "title": "Missing RFC 9116 security.txt Disclosure Policy",
                "severity": "info",
                "confidence": "high",
                "category": "A09: Security Logging & Monitoring",
                "evidence": "Probed standard endpoints '/.well-known/security.txt' and '/security.txt'; no security contact policy was found.",
                "recommendation": "Deploy a 'security.txt' file adhering to RFC 9116 to enable responsible security disclosures."
            })
        else:
            passed.append(f"RFC 9116 security.txt policy active (Contact: {st.get('contact') or st.get('url')})")

        # -------------------------------------------------------------
        # OWASP A01: Sensitive Configuration Exposure (Active Recon Findings)
        # -------------------------------------------------------------
        active_recon = recon.get("active_recon", {})
        sens_files = active_recon.get("sensitive_files", {})
        if sens_files.get("env", {}).get("exposed"):
            findings.append({
                "id": "SEC-EXPOSE-ENV-FILE",
                "finding_key": "exposure.env_file",
                "title": "Exposed Environment Configuration File (/.env)",
                "severity": "critical",
                "confidence": "high",
                "category": "A01: Broken Access Control",
                "evidence": f"GET request to '{origin}/.env' returned HTTP 200 with exposed application environment key assignments.",
                "recommendation": "Block web access to all dotfiles immediately in server configuration."
            })
        if sens_files.get("git_head", {}).get("exposed"):
            findings.append({
                "id": "SEC-EXPOSE-GIT-REPO",
                "finding_key": "exposure.git_repo",
                "title": "Exposed Git Version Control Repository (/.git/HEAD)",
                "severity": "critical",
                "confidence": "high",
                "category": "A01: Broken Access Control",
                "evidence": f"Request to '{origin}/.git/HEAD' confirmed public access to git repository metadata.",
                "recommendation": "Deny all public requests to '/.git' directory trees at the reverse proxy or web server layer."
            })

        # -------------------------------------------------------------
        # OWASP A03: Injection (Safe Evidence-Based SQL Injection Indicators)
        # -------------------------------------------------------------
        # Strictly NO exploit payloads sent!
        # Evaluate response text for database error patterns
        root_content = ""
        metadata = recon.get("metadata", {})
        # Scan HTML text if available in recon
        for pattern in self.DATABASE_ERROR_PATTERNS:
            match = re.search(pattern, str(metadata.get("description", "")) + " " + str(metadata.get("title", "")), re.IGNORECASE)
            if match:
                findings.append({
                    "id": "SEC-INJ-SQL-DB-ERROR",
                    "finding_key": "injection.sql.db_error_leak",
                    "title": "Database Engine Error Pattern Observed in Response",
                    "severity": "high",
                    "confidence": "high",
                    "category": "A03: Injection",
                    "evidence": f"Response contains unhandled database exception pattern: '{match.group(0)}'.",
                    "recommendation": "Disable detailed database error output; implement parameterized queries."
                })
                break

        # Check for dangerous HTTP TRACE method from active recon
        if active_recon.get("trace_method_enabled"):
            findings.append({
                "id": "SEC-HDR-TRACE-ENABLED",
                "finding_key": "http.methods.trace_enabled",
                "title": "HTTP TRACE Method Enabled (Cross-Site Tracing Risk)",
                "severity": "medium",
                "confidence": "high",
                "category": "A05: Security Misconfiguration",
                "evidence": "OPTIONS response includes 'TRACE' in the Allow method header list.",
                "recommendation": "Disable HTTP TRACE method across web server configuration."
            })
        elif active_recon.get("allowed_methods"):
            passed.append(f"HTTP methods inspected (Allow: {', '.join(active_recon['allowed_methods'])})")

        # Robots sensitive paths
        robots = recon.get("robots_txt", {})
        sens_paths = robots.get("sensitive_disallowed_paths", [])
        if sens_paths:
            findings.append({
                "id": "SEC-RECON-ROBOTS-SENSITIVE",
                "finding_key": "recon.robots_txt.sensitive_paths",
                "title": "Sensitive Administrative Routes Disclosed in robots.txt",
                "severity": "low",
                "confidence": "high",
                "category": "A01: Broken Access Control",
                "evidence": f"robots.txt disallow rules explicitly reference internal routes: {', '.join(sens_paths[:4])}.",
                "recommendation": "Do not rely on robots.txt for security; enforce authentication on administrative endpoints."
            })
        elif robots.get("accessible"):
            passed.append(f"robots.txt accessible ({robots.get('rules_count')} lines) with zero sensitive path leaks")

        return findings, passed

    def _normalize_url(self, raw_url: str) -> str:
        url = raw_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        return url


website_auditor = WebsiteAuditor()
