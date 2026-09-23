import re
import time
import urllib.parse
from typing import Dict, Any, List, Tuple, Optional
import httpx
from bs4 import BeautifulSoup
import tldextract

from app.services.risk_engine import risk_engine
from app.services.report_builder import report_builder

class UrlChecker:
    """
    Engine 1: URL Check & Phishing / Redirection / Reputation Analyzer.
    Determines whether a URL looks:
    - safe
    - suspicious
    - phishing-like
    - redirect-heavy
    - malware-linked
    - unreachable / broken
    """

    KNOWN_BRANDS = {
        "paypal": ["paypal.com"],
        "apple": ["apple.com", "icloud.com"],
        "google": ["google.com", "gmail.com", "accounts.google.com"],
        "microsoft": ["microsoft.com", "office.com", "live.com", "outlook.com"],
        "netflix": ["netflix.com"],
        "amazon": ["amazon.com", "amazon.in", "aws.amazon.com"],
        "facebook": ["facebook.com", "fb.com"],
        "instagram": ["instagram.com"],
        "whatsapp": ["whatsapp.com"],
        "binance": ["binance.com"],
        "coinbase": ["coinbase.com"],
        "chase": ["chase.com"],
        "wellsfargo": ["wellsfargo.com"],
        "bankofamerica": ["bankofamerica.com"],
        "sbi": ["onlinesbi.sbi", "sbi.co.in"],
        "hdfc": ["hdfcbank.com"],
        "icici": ["icicibank.com"],
    }

    SUSPICIOUS_TLDS = {
        "top", "xyz", "fit", "work", "click", "buzz", "cfd", "rest", "icu", "monster", "gq", "ml", "cf", "tk", "ga"
    }

    PHISHING_KEYWORDS = [
        "login", "signin", "verify", "verification", "secure", "account", "banking",
        "wallet", "recover", "authenticate", "webscr", "auth-portal", "update-info"
    ]

    DANGEROUS_PAYLOAD_EXTENSIONS = {
        ".exe", ".scr", ".bat", ".cmd", ".msi", ".dll", ".vbs", ".ps1", ".apk",
        ".dmg", ".iso", ".jar", ".hta", ".wsf", ".bin", ".elf", ".pif", ".cpl"
    }

    DANGEROUS_MIME_TYPES = {
        "application/x-msdownload", "application/x-dosexec", "application/x-executable",
        "application/x-msdos-program", "application/x-sh", "application/x-msi"
    }

    async def check_url(self, raw_url: str) -> Tuple[int, str, str, str, List[dict], List[str], dict]:
        """
        Executes comprehensive URL Risk & Phishing Analysis.
        Returns: (risk_score, status, verdict, summary, findings, passed_checks, collected_data)
        """
        url = self._normalize_url(raw_url)
        parsed = urllib.parse.urlsplit(url)
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain

        findings: List[dict] = []
        passed_checks: List[str] = []
        is_unreachable = False

        collected_data: Dict[str, Any] = {
            "input_url": url,
            "domain": domain,
            "subdomain": extracted.subdomain or None,
            "registered_domain": getattr(extracted, "top_domain_under_public_suffix", None) or extracted.registered_domain or domain,
            "tld": extracted.suffix or None,
            "scheme": parsed.scheme,
            "host": parsed.netloc,
            "final_url": url,
            "status_code": None,
            "response_time_ms": None,
            "redirect_chain": [],
            "redirect_hops": 0,
            "is_cross_domain_redirect": False,
            "has_ip_host": False,
            "has_userinfo": False,
            "has_punycode": False,
            "brand_detected": None,
            "page_title": None,
            "has_password_form": False,
        }

        # -------------------------------------------------------------
        # 1. Static Structural & Heuristic Checks
        # -------------------------------------------------------------
        host_no_port = (parsed.hostname or "").lower()

        # Check 1: IP address as host
        is_ip = bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", host_no_port))
        collected_data["has_ip_host"] = is_ip
        if is_ip:
            findings.append({
                "finding_key": "url.heuristics.ip_host",
                "title": "Numeric IP Address Used as Hostname",
                "severity": "high",
                "confidence": "high",
                "category": "URL Structure",
                "evidence": f"URL host is a raw numerical IP address '{host_no_port}' instead of a registered domain. Legitimate online services standardly employ DNS domain names.",
                "recommendation": "Do not enter credentials or download files from raw IP address endpoints."
            })
        else:
            passed_checks.append("Host is a registered domain name (not raw numeric IP)")

        # Check 2: Userinfo (@) in URL authority
        has_at = "@" in parsed.netloc or "@" in url.split("?")[0]
        collected_data["has_userinfo"] = has_at
        if has_at:
            findings.append({
                "finding_key": "url.heuristics.userinfo_spoofing",
                "title": "Deceptive Userinfo '@' Symbol in URL",
                "severity": "critical",
                "confidence": "high",
                "category": "URL Obfuscation",
                "evidence": f"URL contains '@' symbol in authority string: '{url[:100]}'. Modern browsers ignore characters before '@', enabling visual domain deception.",
                "recommendation": "Do not navigate to URLs containing '@' in the host component."
            })
        else:
            passed_checks.append("No deceptive userinfo '@' symbol detected")

        # Check 3: Non-standard suspicious ports
        if parsed.port and parsed.port not in [80, 443, 8000, 3000]:
            findings.append({
                "finding_key": "url.heuristics.suspicious_port",
                "title": "Non-Standard Port Specified in URL",
                "severity": "medium",
                "confidence": "high",
                "category": "URL Structure",
                "evidence": f"URL directs traffic to non-standard port :{parsed.port}. Commonly used by phishing kits or unauthorized staging relays.",
                "recommendation": "Verify whether the target service operates on this non-standard port."
            })
        else:
            passed_checks.append("Standard web transport ports in use (80/443)")

        # Check 4: Punycode / IDN Homograph Obfuscation
        has_puny = "xn--" in host_no_port
        collected_data["has_punycode"] = has_puny
        if has_puny:
            findings.append({
                "finding_key": "url.heuristics.punycode_homograph",
                "title": "Punycode (IDN) Character Encoding Detected",
                "severity": "high",
                "confidence": "high",
                "category": "Homograph Spoofing",
                "evidence": f"Hostname '{host_no_port}' utilizes Punycode ('xn--') internationalized encoding. Attackers frequently use lookalike Cyrillic/Greek characters to spoof trusted domains.",
                "recommendation": "Confirm the genuine Latin spelling of the target domain."
            })
        else:
            passed_checks.append("Standard ASCII domain characters (no Punycode homograph encoding)")

        # Check 5: Excessive Subdomains
        subdomain_parts = [p for p in extracted.subdomain.split(".") if p]
        if len(subdomain_parts) >= 3:
            findings.append({
                "finding_key": "url.heuristics.excessive_subdomains",
                "title": "Excessive Subdomain Stacking",
                "severity": "medium",
                "confidence": "high",
                "category": "URL Structure",
                "evidence": f"Hostname contains {len(subdomain_parts)} nested subdomains ('{extracted.subdomain}'). Used to hide malicious domains beyond the mobile browser address bar view.",
                "recommendation": "Verify the parent registered domain before interacting with the site."
            })
        else:
            passed_checks.append("Domain hierarchy depth is within normal parameters")

        # Check 6: Lookalike Brand Impersonation
        reg_domain = (getattr(extracted, "top_domain_under_public_suffix", None) or extracted.registered_domain or "").lower()
        full_url_lower = url.lower()
        impersonated_brand = None

        for brand, legitimate_domains in self.KNOWN_BRANDS.items():
            # If brand appears in subdomain, path, or domain name
            if brand in full_url_lower:
                if reg_domain not in legitimate_domains:
                    impersonated_brand = brand
                    collected_data["brand_detected"] = brand
                    findings.append({
                        "finding_key": f"url.phishing.brand_impersonation.{brand}",
                        "title": f"Potential Brand Impersonation: '{brand.capitalize()}'",
                        "severity": "critical",
                        "confidence": "high",
                        "category": "Brand Protection",
                        "evidence": f"URL incorporates brand identifier '{brand}', but registered domain '{reg_domain}' is not recognized as authentic {brand.capitalize()} infrastructure.",
                        "recommendation": f"Do not enter {brand.capitalize()} account credentials. Access the legitimate service directly via its authentic domain."
                    })
                    break

        if not impersonated_brand:
            passed_checks.append("Zero recognized brand lookalike / typosquatting patterns detected")

        # Check 7: Phishing Keywords with Suspicious TLD
        tld_lower = (extracted.suffix or "").lower()
        matched_keywords = [kw for kw in self.PHISHING_KEYWORDS if kw in full_url_lower]
        if matched_keywords and tld_lower in self.SUSPICIOUS_TLDS and not impersonated_brand:
            findings.append({
                "finding_key": "url.phishing.suspicious_tld_combination",
                "title": "Authentication Keywords on High-Risk TLD",
                "severity": "high",
                "confidence": "high",
                "category": "Phishing Heuristics",
                "evidence": f"URL combines sensitive keyword(s) {matched_keywords[:3]} with high-abuse TLD '.{tld_lower}' under domain '{reg_domain}'.",
                "recommendation": "Exercise extreme caution before submitting any personal information or credentials."
            })

        # Check 8: Malware & Executable Payload File Link
        url_path_lower = parsed.path.lower()
        query_lower = parsed.query.lower()
        detected_ext = None
        for ext in self.DANGEROUS_PAYLOAD_EXTENSIONS:
            if url_path_lower.endswith(ext) or f"{ext}?" in url.lower() or f"={ext}" in query_lower:
                detected_ext = ext
                break

        collected_data["has_malware_extension"] = bool(detected_ext)
        if detected_ext:
            findings.append({
                "finding_key": "url.malware.executable_file_link",
                "title": f"Direct Malware / Executable Payload Link ('{detected_ext}')",
                "severity": "critical",
                "confidence": "high",
                "category": "Malware Protection",
                "evidence": f"URL targets a direct executable software file '{detected_ext}' in path '{parsed.path}'. Attackers deploy direct links to drop trojans, spyware, or ransomware.",
                "recommendation": "Do not download, open, or execute files from unverified online links."
            })
        else:
            passed_checks.append("URL path does not target direct executable (.exe/.msi/.scr) payloads")

        # -------------------------------------------------------------
        # 2. Live Network Probing & Redirection Analysis
        # -------------------------------------------------------------
        start_time = time.time()
        try:
            async with httpx.AsyncClient(
                timeout=9.0,
                follow_redirects=True,
                verify=False,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AegisScan-URLRiskCheck/1.0"
                }
            ) as client:
                resp = await client.get(url)
                duration_ms = int((time.time() - start_time) * 1000)
                collected_data["response_time_ms"] = duration_ms
                collected_data["status_code"] = resp.status_code
                collected_data["final_url"] = str(resp.url)

                # Capture Redirection Chain
                chain = [str(r.url) for r in resp.history] + [str(resp.url)]
                hops = len(resp.history)
                collected_data["redirect_chain"] = chain
                collected_data["redirect_hops"] = hops

                passed_checks.append(f"Target host reachable and responsive (HTTP {resp.status_code} in {duration_ms}ms)")

                # Redirection hop evaluation
                if hops >= 3:
                    findings.append({
                        "finding_key": "url.redirect.excessive_hops",
                        "title": "Excessive Redirection Chain (Redirect-Heavy)",
                        "severity": "medium",
                        "confidence": "high",
                        "category": "Redirection Safety",
                        "evidence": f"URL traversed {hops} redirection hops: {' -> '.join(chain)}.",
                        "recommendation": "Excessive redirection chains are commonly used in traffic distribution systems to bypass URL security filters."
                    })
                elif hops > 0:
                    passed_checks.append(f"Handled {hops} standard HTTP redirect hop(s) safely")

                # Cross-domain redirection check
                final_extracted = tldextract.extract(str(resp.url))
                final_reg = getattr(final_extracted, "top_domain_under_public_suffix", None) or final_extracted.registered_domain
                if reg_domain and final_reg and reg_domain != final_reg:
                    collected_data["is_cross_domain_redirect"] = True
                    findings.append({
                        "finding_key": "url.redirect.cross_domain",
                        "title": "Cross-Domain Destination Redirection",
                        "severity": "medium",
                        "confidence": "high",
                        "category": "Redirection Safety",
                        "evidence": f"Initial target domain '{reg_domain}' redirected to an external domain '{final_reg}' (final URL: {resp.url}).",
                        "recommendation": f"Verify that you intended to navigate to '{final_reg}'."
                    })
                else:
                    passed_checks.append("Redirection destination remains within original host domain boundary")

                # -------------------------------------------------------------
                # 3. Payload & HTML Content Inspection (Malware & Phishing)
                # -------------------------------------------------------------
                content_type = resp.headers.get("content-type", "").lower()
                content_disp = resp.headers.get("content-disposition", "").lower()

                # Check if response delivers binary executable payload
                has_mime_payload = any(m in content_type for m in self.DANGEROUS_MIME_TYPES)
                has_disp_payload = any(ext in content_disp for ext in self.DANGEROUS_PAYLOAD_EXTENSIONS)
                if has_mime_payload or has_disp_payload:
                    collected_data["has_malware_extension"] = True
                    findings.append({
                        "finding_key": "url.malware.executable_mime_payload",
                        "title": "Direct Executable / Malware Binary Payload Delivery",
                        "severity": "critical",
                        "confidence": "high",
                        "category": "Malware Protection",
                        "evidence": f"Server response delivers binary software executable payload (Content-Type: '{content_type}', Content-Disposition: '{content_disp}').",
                        "recommendation": "Do not execute or launch software downloaded from unverified link destinations."
                    })
                else:
                    passed_checks.append("Server response Content-Type is standard web document (no executable payload delivery)")
                if "text/html" in content_type:
                    try:
                        soup = BeautifulSoup(resp.text[:250000], "html.parser")
                        title_tag = soup.find("title")
                        if title_tag and title_tag.string:
                            collected_data["page_title"] = title_tag.string.strip()[:100]

                        # Check for password inputs
                        password_inputs = soup.find_all("input", attrs={"type": re.compile(r"password", re.I)})
                        has_pw = len(password_inputs) > 0
                        collected_data["has_password_form"] = has_pw

                        if has_pw and (impersonated_brand or is_ip):
                            findings.append({
                                "finding_key": "url.phishing.credential_harvesting_form",
                                "title": "Credential Harvesting Login Form on Unverified Host",
                                "severity": "critical",
                                "confidence": "high",
                                "category": "Phishing Protection",
                                "evidence": f"Found password authentication input form on unverified/suspicious host '{resp.url.host}'. Form targets: {password_inputs[0].parent.get('action') or '[Self]'}.",
                                "recommendation": "Never submit passwords or sensitive information on unverified domain infrastructure."
                            })
                        elif has_pw and resp.url.scheme == "http":
                            findings.append({
                                "finding_key": "url.html.password_over_http",
                                "title": "Password Input Field Served Over Plain HTTP",
                                "severity": "critical",
                                "confidence": "high",
                                "category": "Transport Layer Security",
                                "evidence": f"Page at '{resp.url}' renders password input elements over unencrypted plain HTTP transport.",
                                "recommendation": "Enforce HTTPS to prevent credentials from being captured in plaintext over the wire."
                            })
                    except Exception:
                        pass

        except httpx.RequestError as e:
            is_unreachable = True
            findings.append({
                "finding_key": "url.network.unreachable",
                "title": "Target URL Unreachable / Connection Failed",
                "severity": "high",
                "confidence": "high",
                "category": "Connectivity",
                "evidence": f"Live connection probe to '{url}' failed: {str(e)[:160]}",
                "recommendation": "Verify network routing, DNS records, and host server availability."
            })

        # -------------------------------------------------------------
        # 4. Scoring, Verdict & Report Compilation
        # -------------------------------------------------------------
        risk_score = risk_engine.compute_score(findings)
        status_label = risk_engine.classify_status(risk_score)
        verdict = risk_engine.classify_url_verdict(
            score=risk_score,
            findings=findings,
            is_unreachable=is_unreachable,
            redirect_hops=collected_data.get("redirect_hops", 0)
        )

        # Threat verdict classification: Phishing vs Malware vs Clean
        keys = [f.get("finding_key", "").lower() for f in findings]
        is_phishing = any(
            ("phishing" in k or "impersonation" in k or "credential" in k or "userinfo" in k)
            for k in keys
        )
        is_malware = any(
            ("malware" in k or "executable" in k or "payload" in k)
            for k in keys
        )
        is_cross_domain = collected_data.get("is_cross_domain_redirect", False)
        is_suspicious = (not is_phishing and not is_malware) and (
            risk_score >= 30 or
            is_cross_domain or
            collected_data.get("has_punycode", False) or
            collected_data.get("redirect_hops", 0) >= 3
        )
        is_clean = not is_phishing and not is_malware and not is_suspicious and not is_unreachable

        phishing_verdict = "PHISHING DETECTED" if is_phishing else "NO PHISHING DETECTED"
        malware_verdict = "MALWARE / VIRUS RISK" if is_malware else "NO VIRUS / MALWARE DETECTED"

        overall_threat = (
            "PHISHING" if is_phishing else
            "MALWARE" if is_malware else
            "SUSPICIOUS" if is_suspicious else
            "UNREACHABLE" if is_unreachable else
            "SAFE"
        )

        # Extract final domain cleanly for reporting
        dest_reg = (
            final_reg if "final_reg" in locals() and final_reg
            else reg_domain
        )

        collected_data["threat_analysis"] = {
            "is_phishing": is_phishing,
            "is_malware": is_malware,
            "is_suspicious": is_suspicious,
            "is_clean": is_clean,
            "is_unreachable": is_unreachable,
            "phishing_verdict": phishing_verdict,
            "malware_verdict": malware_verdict,
            "overall_verdict": overall_threat,
            "impersonated_brand": collected_data.get("brand_detected"),
            "has_credential_form": collected_data.get("has_password_form", False),
            "has_malware_extension": collected_data.get("has_malware_extension", False),
            "is_cross_domain_redirect": is_cross_domain,
            "redirect_hops": collected_data.get("redirect_hops", 0),
            "redirect_chain": collected_data.get("redirect_chain", []),
            "input_url": url,
            "final_url": collected_data.get("final_url", url),
            "domain": domain,
            "registered_domain": reg_domain,
            "final_registered_domain": dest_reg,
            "status_code": collected_data.get("status_code"),
            "response_time_ms": collected_data.get("response_time_ms"),
        }

        # Build focused, clear executive summary tailored directly to URL Threat Analysis
        if is_phishing:
            brand_str = f" targeting '{collected_data.get('brand_detected').capitalize()}'" if collected_data.get("brand_detected") else ""
            summary = f"URL Threat Alert: High-risk phishing indicators detected on '{url}'{brand_str}. Deceptive domain structures or unauthenticated credential harvesting forms were observed."
        elif is_malware:
            summary = f"URL Threat Alert: Malicious software / virus payload delivery detected on '{url}'. The link targets or delivers binary executable files."
        elif is_unreachable:
            summary = f"URL Threat Check: Target host '{url}' is unreachable or failed DNS/connection resolution."
        elif is_cross_domain:
            summary = f"URL Threat Analysis for '{url}': No phishing patterns detected. No malicious software or virus payloads detected. Note: Destination redirects to '{dest_reg}'."
        else:
            summary = f"URL Threat Analysis for '{url}': Clean & Safe. No phishing patterns detected. No virus or malicious software payloads identified across {len(passed_checks)} verified safety checks."

        return risk_score, status_label, verdict, summary, findings, passed_checks, collected_data

    def _normalize_url(self, raw_url: str) -> str:
        url = raw_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        return url


url_checker = UrlChecker()
