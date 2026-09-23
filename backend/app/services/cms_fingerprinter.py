import re
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
import httpx

class CmsFingerprinter:
    """
    Dedicated CMS, Technology Stack & Infrastructure Fingerprinter.
    Performs passive detection and non-invasive presence verification for:
    - WordPress / WordPress.com
    - Drupal
    - Joomla
    - Shopify
    - Wix
    - Squarespace
    - Ghost
    - Custom PHP / Node / Python / ASP.NET Stacks
    - Web Servers (Nginx, Apache, Cloudflare, LiteSpeed)
    - Client Libraries (jQuery, React, Vue, Next.js)
    """

    async def inspect_cms(
        self,
        html_text: str,
        response_headers: Dict[str, str],
        client: httpx.AsyncClient,
        origin: str
    ) -> Tuple[Dict[str, Any], List[dict], List[str]]:
        """
        Passively inspects HTML and headers, followed by non-invasive presence checks.
        Returns: (cms_details, findings, passed_checks)
        """
        findings: List[dict] = []
        passed_checks: List[str] = []

        headers_lower = {k.lower(): v for k, v in response_headers.items()}
        soup = BeautifulSoup(html_text[:500000], "html.parser") if html_text else None

        detected_cms: Optional[str] = None
        cms_version: Optional[str] = None
        platform_type: str = "Self-Hosted / Custom"
        signatures_observed: List[str] = []
        detected_plugins: List[str] = []
        detected_themes: List[str] = []
        libraries_detected: List[str] = []

        # -------------------------------------------------------------
        # 1. Web Server & Backend Runtime Fingerprinting
        # -------------------------------------------------------------
        server_header = headers_lower.get("server", "").strip()
        web_server = server_header if server_header else "Not disclosed"

        powered_by = headers_lower.get("x-powered-by", "").strip()
        backend_runtime = powered_by if powered_by else "Not disclosed"

        # -------------------------------------------------------------
        # 2. Meta Generator Inspection
        # -------------------------------------------------------------
        generator_content = ""
        if soup:
            gen_meta = soup.find("meta", attrs={"name": re.compile(r"^generator$", re.I)})
            if gen_meta and gen_meta.get("content"):
                generator_content = str(gen_meta.get("content")).strip()

        # -------------------------------------------------------------
        # 3. CMS Pattern Matching
        # -------------------------------------------------------------
        # A. WordPress / WordPress.com
        is_wp = False
        wp_ver_match = re.search(r"WordPress\s*([\d\.]+)?", generator_content, re.IGNORECASE)
        if wp_ver_match or "wp-content" in html_text or "wp-includes" in html_text or "wp-json" in html_text:
            is_wp = True
            detected_cms = "WordPress"
            if "wordpress.com" in html_text.lower() or "s0.wp.com" in html_text or "x-hacker" in headers_lower:
                platform_type = "WordPress.com Managed"
            else:
                platform_type = "WordPress"

            if wp_ver_match and wp_ver_match.group(1):
                cms_version = wp_ver_match.group(1)
                signatures_observed.append(f"Meta Generator: '{generator_content}'")
            elif "wp-content" in html_text:
                signatures_observed.append("HTML structure references /wp-content/ asset paths")

            # Extract plugins from asset URLs
            plugin_matches = re.findall(r"/wp-content/plugins/([a-zA-Z0-9_\-\.]+)/", html_text)
            if plugin_matches:
                unique_plugins = list(dict.fromkeys(plugin_matches))[:8]
                detected_plugins = unique_plugins

            # Extract theme from asset URLs
            theme_matches = re.findall(r"/wp-content/themes/([a-zA-Z0-9_\-\.]+)/", html_text)
            if theme_matches:
                detected_themes = list(dict.fromkeys(theme_matches))[:4]

        # B. Drupal
        elif "drupal" in generator_content.lower() or "drupal.js" in html_text or "x-drupal-cache" in headers_lower or "sites/default/files" in html_text:
            detected_cms = "Drupal"
            platform_type = "Drupal"
            d_ver = re.search(r"Drupal\s*([\d\.]+)?", generator_content, re.IGNORECASE)
            if d_ver and d_ver.group(1):
                cms_version = d_ver.group(1)
                signatures_observed.append(f"Meta Generator: '{generator_content}'")
            else:
                signatures_observed.append("Drupal core JS asset paths or headers observed")

        # C. Joomla
        elif "joomla" in generator_content.lower() or "/media/jui/" in html_text or "/media/system/js/" in html_text:
            detected_cms = "Joomla"
            platform_type = "Joomla"
            j_ver = re.search(r"Joomla!\s*([\d\.]+)?", generator_content, re.IGNORECASE)
            if j_ver and j_ver.group(1):
                cms_version = j_ver.group(1)
                signatures_observed.append(f"Meta Generator: '{generator_content}'")
            else:
                signatures_observed.append("Joomla UI and system script assets observed")

        # D. Shopify
        elif "cdn.shopify.com" in html_text or "myshopify.com" in html_text or "x-shopid" in headers_lower:
            detected_cms = "Shopify"
            platform_type = "Shopify Cloud E-Commerce"
            signatures_observed.append("Shopify CDN assets and script bindings detected")

        # E. Wix
        elif "static.parastorage.com" in html_text or "wix.com" in html_text or "x-wix-renderer-server" in headers_lower:
            detected_cms = "Wix"
            platform_type = "Wix Cloud Platform"
            signatures_observed.append("Wix parastorage static CDN references detected")

        # F. Squarespace
        elif "static1.squarespace.com" in html_text or "squarespace.constants" in html_text.lower():
            detected_cms = "Squarespace"
            platform_type = "Squarespace Hosted Platform"
            signatures_observed.append("Squarespace static CDN and constant namespaces observed")

        # G. Ghost
        elif "ghost" in generator_content.lower() or "ghost-search" in html_text:
            detected_cms = "Ghost"
            platform_type = "Ghost Headless / Blog"
            signatures_observed.append("Ghost generator meta tag or search assets observed")

        # H. HubSpot CMS
        elif "hs-script-loader" in html_text or "_hsq" in html_text or "hubspot.com" in html_text:
            detected_cms = "HubSpot CMS"
            platform_type = "HubSpot Cloud CMS"
            signatures_observed.append("HubSpot analytics or script loader bindings observed")

        # I. Magento / Adobe Commerce
        elif "mage.cookies" in html_text.lower() or "/skin/frontend/" in html_text or "mage/cookies.js" in html_text:
            detected_cms = "Magento"
            platform_type = "Adobe Commerce / Magento"
            signatures_observed.append("Magento frontend cookie namespaces or assets observed")

        # J. PrestaShop
        elif "prestashop" in html_text.lower() or "/modules/prestashop" in html_text:
            detected_cms = "PrestaShop"
            platform_type = "PrestaShop E-Commerce"
            signatures_observed.append("PrestaShop asset paths or namespaces observed")

        # K. Hugo
        elif "hugo" in generator_content.lower():
            detected_cms = "Hugo"
            platform_type = "Static Site Generator (Hugo)"
            h_ver = re.search(r"Hugo\s*([\d\.]+)?", generator_content, re.IGNORECASE)
            if h_ver and h_ver.group(1):
                cms_version = h_ver.group(1)
            signatures_observed.append(f"Meta Generator: '{generator_content}'")

        # L. Gatsby
        elif "id=\"___gatsby\"" in html_text or "gatsby-image" in html_text or "gatsby" in generator_content.lower():
            detected_cms = "Gatsby"
            platform_type = "Static / Headless (Gatsby)"
            signatures_observed.append("Gatsby hydration container or asset bindings observed")

        # M. Astro
        elif "astro-island" in html_text or "astro" in generator_content.lower():
            detected_cms = "Astro"
            platform_type = "Modern Islands Architecture (Astro)"
            signatures_observed.append("Astro custom elements or generator signature observed")

        # N. Docusaurus
        elif "docusaurus" in generator_content.lower() or "docusaurus" in html_text.lower():
            detected_cms = "Docusaurus"
            platform_type = "Documentation Platform (Docusaurus)"
            signatures_observed.append("Docusaurus generator or styling markers observed")

        # -------------------------------------------------------------
        # 4. Libraries & Frontend Frameworks Detection
        if not detected_cms:
            if "/wp-content/" in html_text or "/wp-includes/" in html_text:
                detected_cms = "WordPress"
                is_wp = True
            elif "cdn.shopify.com" in html_text or "Shopify.theme" in html_text:
                detected_cms = "Shopify"
                platform_type = "SaaS / Hosted E-Commerce"
            elif "static.wixstatic.com" in html_text or "wix-warmup-data" in html_text:
                detected_cms = "Wix"
                platform_type = "SaaS / Hosted Builder"
            elif "static1.squarespace.com" in html_text:
                detected_cms = "Squarespace"
                platform_type = "SaaS / Hosted Builder"
            elif "drupal.js" in html_text or "/sites/default/files" in html_text:
                detected_cms = "Drupal"
        else:
            is_wp = detected_cms == "WordPress"

        # Check WordPress.com managed cloud signatures
        if is_wp or detected_cms == "WordPress":
            if "s0.wp.com" in html_text or "pixel.wp.com" in html_text or "wp.com" in server_header.lower():
                platform_type = "Managed WordPress.com Cloud"
                signatures_observed.append("WordPress.com Managed Assets / Infrastructure")

        # Extract WordPress Plugins & Themes if present
        if is_wp or detected_cms == "WordPress":
            plugin_matches = re.findall(r"/wp-content/plugins/([a-zA-Z0-9_\-]+)/", html_text)
            detected_plugins = sorted(list(set(plugin_matches)))
            theme_matches = re.findall(r"/wp-content/themes/([a-zA-Z0-9_\-]+)/", html_text)
            detected_themes = sorted(list(set(theme_matches)))

        # -------------------------------------------------------------
        # 4. Tech Stack & Wappalyzer-Style Categorized Profile
        # -------------------------------------------------------------
        tech_profile: Dict[str, List[Dict[str, Any]]] = {}

        def add_tech(cat: str, name: str, ver: Optional[str] = None, conf: str = "high"):
            if cat not in tech_profile:
                tech_profile[cat] = []
            if not any(t["name"].lower() == name.lower() for t in tech_profile[cat]):
                tech_profile[cat].append({
                    "name": name,
                    "version": ver,
                    "confidence": conf,
                    "category": cat
                })

        # Category: CMS & Platforms
        if detected_cms and detected_cms != "Custom / Jamstack":
            add_tech("CMS & Platforms", detected_cms, cms_version, "high")
        elif "assets.website-files.com" in html_text or "w-nav" in html_text:
            add_tech("CMS & Platforms", "Webflow", None, "high")
            detected_cms = "Webflow"

        # Category: Web Servers
        if server_header:
            srv_lower = server_header.lower()
            if "nginx" in srv_lower:
                v = re.search(r"nginx/([\d\.]+)", server_header, re.I)
                add_tech("Web Servers", "Nginx", v.group(1) if v else None, "high")
                if "Nginx" not in signatures_observed:
                    signatures_observed.append("Nginx")
            elif "apache" in srv_lower:
                v = re.search(r"apache/([\d\.]+)", server_header, re.I)
                add_tech("Web Servers", "Apache", v.group(1) if v else None, "high")
                if "Apache" not in signatures_observed:
                    signatures_observed.append("Apache")
            elif "litespeed" in srv_lower:
                add_tech("Web Servers", "LiteSpeed", None, "high")
                if "LiteSpeed" not in signatures_observed:
                    signatures_observed.append("LiteSpeed")
            elif "caddy" in srv_lower:
                add_tech("Web Servers", "Caddy", None, "high")
                if "Caddy" not in signatures_observed:
                    signatures_observed.append("Caddy")
            elif "openresty" in srv_lower:
                add_tech("Web Servers", "OpenResty", None, "high")
                if "OpenResty" not in signatures_observed:
                    signatures_observed.append("OpenResty")
            elif "microsoft-iis" in srv_lower:
                v = re.search(r"microsoft-iis/([\d\.]+)", server_header, re.I)
                add_tech("Web Servers", "Microsoft-IIS", v.group(1) if v else None, "high")
            elif "cloudflare" in srv_lower:
                add_tech("Web Servers", "Cloudflare", None, "high")
                if "Cloudflare" not in signatures_observed:
                    signatures_observed.append("Cloudflare")
            elif "gws" in srv_lower or "gse" in srv_lower:
                add_tech("Web Servers", "Google Web Server (GWS)", None, "high")
            elif "amazons3" in srv_lower:
                add_tech("Web Servers", "Amazon S3", None, "high")

        # Category: Backend Runtimes & Frameworks
        if powered_by:
            pb_lower = powered_by.lower()
            if "php" in pb_lower:
                v = re.search(r"php/([\d\.]+)", powered_by, re.I)
                add_tech("Backend Runtimes", "PHP", v.group(1) if v else None, "high")
                if "PHP" not in signatures_observed:
                    signatures_observed.append("PHP")
            elif "express" in pb_lower or "node" in pb_lower:
                add_tech("Backend Runtimes", "Node.js (Express)", None, "high")
            elif "asp.net" in pb_lower:
                add_tech("Backend Runtimes", "ASP.NET", None, "high")
        elif "php" in backend_runtime.lower() or "phpsessid" in str(response_headers).lower():
            add_tech("Backend Runtimes", "PHP", None, "medium")
            if "PHP" not in signatures_observed:
                signatures_observed.append("PHP")

        # Additional passive runtime signals
        if "csrftoken" in str(response_headers).lower() or "django" in html_text.lower():
            add_tech("Backend Runtimes", "Python (Django)", None, "medium")
        elif "flask" in server_header.lower() or "flask" in html_text.lower():
            add_tech("Backend Runtimes", "Python (Flask)", None, "medium")
        elif "fastapi" in html_text.lower() or "x-fastapi" in headers_lower:
            add_tech("Backend Runtimes", "Python (FastAPI)", None, "high")

        if "csrf-param" in html_text or "authenticity_token" in html_text or "action_dispatch" in html_text:
            add_tech("Backend Runtimes", "Ruby on Rails", None, "high")

        if "jsessionid" in str(response_headers).lower() or "x-application-context" in headers_lower:
            add_tech("Backend Runtimes", "Java (Spring)", None, "high")

        # Category: JavaScript Frameworks & Libraries
        if "_next/static" in html_text or "__NEXT_DATA__" in html_text:
            add_tech("JavaScript Frameworks", "Next.js", None, "high")
            add_tech("JavaScript Frameworks", "React", None, "high")
            libraries_detected.append("Next.js")
            libraries_detected.append("React")
        elif "react" in html_text.lower() or "data-reactroot" in html_text:
            add_tech("JavaScript Frameworks", "React", None, "high")
            libraries_detected.append("React")

        if "_nuxt" in html_text or "__NUXT__" in html_text:
            add_tech("JavaScript Frameworks", "Nuxt.js", None, "high")
            add_tech("JavaScript Frameworks", "Vue.js", None, "high")
            libraries_detected.append("Nuxt.js")
            libraries_detected.append("Vue.js")
        elif "vue.js" in html_text.lower() or "data-v-" in html_text:
            add_tech("JavaScript Frameworks", "Vue.js", None, "high")
            libraries_detected.append("Vue.js")

        if "ng-version" in html_text or "ng-app" in html_text:
            add_tech("JavaScript Frameworks", "Angular", None, "high")
            libraries_detected.append("Angular")

        if "__sveltekit" in html_text or "svelte-" in html_text:
            add_tech("JavaScript Frameworks", "Svelte", None, "high")
            libraries_detected.append("Svelte")

        if "x-data=" in html_text or "alpinejs" in html_text.lower():
            add_tech("JavaScript Frameworks", "Alpine.js", None, "high")
            libraries_detected.append("Alpine.js")

        if "hx-get=" in html_text or "hx-post=" in html_text or "htmx.org" in html_text:
            add_tech("JavaScript Frameworks", "HTMX", None, "high")
            libraries_detected.append("HTMX")

        if "jquery" in html_text.lower():
            jq_match = re.search(r"jquery[.-]([\d\.]+)(?:\.min)?\.js", html_text, re.IGNORECASE)
            jq_ver = jq_match.group(1) if jq_match else None
            add_tech("JavaScript Libraries", "jQuery", jq_ver, "high")
            libraries_detected.append(f"jQuery {jq_ver}" if jq_ver else "jQuery")

        # Category: UI Frameworks & Styling
        if "tailwind" in html_text.lower():
            add_tech("UI Frameworks", "Tailwind CSS", None, "high")
            libraries_detected.append("Tailwind CSS")
        if "bootstrap.min.css" in html_text or "bootstrap.bundle" in html_text:
            add_tech("UI Frameworks", "Bootstrap", None, "high")
            libraries_detected.append("Bootstrap")
        if "font-awesome" in html_text.lower() or "fontawesome" in html_text.lower():
            add_tech("UI Frameworks", "Font Awesome", None, "high")
        if "muibutton" in html_text.lower() or "mui-" in html_text:
            add_tech("UI Frameworks", "Material UI", None, "high")
        if "bulma.min.css" in html_text or "is-primary" in html_text:
            add_tech("UI Frameworks", "Bulma", None, "medium")

        # Category: Analytics & Telemetry
        if "googletagmanager.com" in html_text or "gtag(" in html_text or "google-analytics.com" in html_text:
            add_tech("Analytics & Telemetry", "Google Analytics / GTM", None, "high")
            libraries_detected.append("Google Analytics / GTM")
        if "static.hotjar.com" in html_text or "_hjSettings" in html_text:
            add_tech("Analytics & Telemetry", "Hotjar", None, "high")
            libraries_detected.append("Hotjar")
        if "cdn.segment.com" in html_text:
            add_tech("Analytics & Telemetry", "Segment", None, "high")
            libraries_detected.append("Segment")
        if "browser.sentry-cdn.com" in html_text:
            add_tech("Analytics & Telemetry", "Sentry", None, "high")
        if "api.mixpanel.com" in html_text or "mixpanel.init" in html_text:
            add_tech("Analytics & Telemetry", "Mixpanel", None, "high")
        if "amplitude.com" in html_text:
            add_tech("Analytics & Telemetry", "Amplitude", None, "high")
        if "plausible.io" in html_text:
            add_tech("Analytics & Telemetry", "Plausible", None, "high")
        if "posthog.com" in html_text or "posthog.init" in html_text:
            add_tech("Analytics & Telemetry", "PostHog", None, "high")
        if "cloudflareinsights.com/beacon" in html_text:
            add_tech("Analytics & Telemetry", "Cloudflare Web Analytics", None, "high")

        # Category: CDN & Infrastructure
        if "cf-ray" in headers_lower or "cloudflare" in server_header.lower():
            add_tech("CDN & Infrastructure", "Cloudflare", None, "high")
        if "x-amz-cf-id" in headers_lower or "cloudfront.net" in html_text:
            add_tech("CDN & Infrastructure", "Amazon CloudFront", None, "high")
        if "x-fastly-request-id" in headers_lower or "fastly" in headers_lower.get("server", "").lower():
            add_tech("CDN & Infrastructure", "Fastly", None, "high")
        if "x-vercel-id" in headers_lower:
            add_tech("CDN & Infrastructure", "Vercel", None, "high")
        if "x-nf-request-id" in headers_lower or "netlify" in server_header.lower():
            add_tech("CDN & Infrastructure", "Netlify", None, "high")
        if "x-akamai-transformed" in headers_lower or "akamai" in server_header.lower():
            add_tech("CDN & Infrastructure", "Akamai", None, "high")
        if "github.io" in html_text or "github-pages" in server_header.lower():
            add_tech("CDN & Infrastructure", "GitHub Pages", None, "high")

        # Category: Payment Processors & E-Commerce
        if "js.stripe.com" in html_text:
            add_tech("Payment Processors", "Stripe", None, "high")
        if "paypal.com/sdk" in html_text or "paypalobjects.com" in html_text:
            add_tech("Payment Processors", "PayPal", None, "high")
        if "checkout.razorpay.com" in html_text:
            add_tech("Payment Processors", "Razorpay", None, "high")
        if "squareup.com" in html_text or "square.js" in html_text:
            add_tech("Payment Processors", "Square", None, "high")
        if "shopify-pay" in html_text:
            add_tech("Payment Processors", "Shopify Pay", None, "high")
        if "klarna.com" in html_text:
            add_tech("Payment Processors", "Klarna", None, "high")

        # Category: Security & Cloud Shields
        if "cf-ray" in headers_lower:
            add_tech("Security & Cloud Shields", "Cloudflare Edge Shield", None, "high")
        if "x-amzn-waf-action" in headers_lower or "awswaf" in str(response_headers).lower():
            add_tech("Security & Cloud Shields", "AWS WAF", None, "high")
        if "x-cdn" in headers_lower and "incapsula" in headers_lower["x-cdn"].lower():
            add_tech("Security & Cloud Shields", "Imperva Incapsula WAF", None, "high")
        if "x-sucuri-id" in headers_lower or "x-sucuri-cache" in headers_lower:
            add_tech("Security & Cloud Shields", "Sucuri CloudProxy", None, "high")

        # -------------------------------------------------------------
        # 5. Non-Invasive Passive Presence Checks (Strictly Presence Only)
        # -------------------------------------------------------------
        login_path_detected: Optional[str] = None
        login_path_probe: Optional[Dict[str, Any]] = None
        xmlrpc_detected: bool = False
        xmlrpc_probe: Optional[Dict[str, Any]] = None

        if client and origin:
            if is_wp:
                # Check /wp-login.php (3.0s timeout, non-invasive GET probe)
                wp_login_url = f"{origin}/wp-login.php"
                try:
                    probe_login = await client.get(wp_login_url, timeout=3.0)
                    is_accessible = (probe_login.status_code == 200 and ("login" in probe_login.text.lower() or "user_login" in probe_login.text))
                    login_path_probe = {
                        "tested_path": "/wp-login.php",
                        "accessible": is_accessible,
                        "status_code": probe_login.status_code,
                        "redirected": probe_login.status_code in [301, 302]
                    }
                    if is_accessible:
                        login_path_detected = f"{wp_login_url} (HTTP 200)"
                        findings.append({
                            "finding_key": "cms.wordpress.login_exposed",
                            "title": "Default WordPress Login Portal Accessible",
                            "severity": "low",
                            "confidence": "high",
                            "category": "CMS Exposure",
                            "evidence": f"Default login portal '{wp_login_url}' returned HTTP 200. Automated bots target this standard path for brute-force attacks.",
                            "recommendation": "Protect /wp-login.php with rate limiting, IP whitelisting, HTTP basic auth, or a custom login slug."
                        })
                    elif probe_login.status_code in [301, 302]:
                        login_path_detected = f"{wp_login_url} (Redirects to {probe_login.headers.get('location', '')})"
                except Exception:
                    pass

                # Check /xmlrpc.php (3.0s timeout, non-invasive GET probe)
                xmlrpc_url = f"{origin}/xmlrpc.php"
                try:
                    probe_xmlrpc = await client.get(xmlrpc_url, timeout=3.0)
                    is_xmlrpc_active = (probe_xmlrpc.status_code in [200, 405] and "XML-RPC" in probe_xmlrpc.text) or (probe_xmlrpc.status_code == 200)
                    xmlrpc_probe = {
                        "tested_path": "/xmlrpc.php",
                        "accessible": is_xmlrpc_active,
                        "status_code": probe_xmlrpc.status_code
                    }
                    if is_xmlrpc_active:
                        xmlrpc_detected = True
                        findings.append({
                            "finding_key": "cms.wordpress.xmlrpc_active",
                            "title": "WordPress XML-RPC API Exposed",
                            "severity": "medium",
                            "confidence": "high",
                            "category": "CMS Exposure",
                            "evidence": f"Endpoint '{xmlrpc_url}' is accessible (HTTP {probe_xmlrpc.status_code}: '{probe_xmlrpc.text.strip()[:100]}'). XML-RPC is frequently abused for brute-force amplification and DDoS reflection.",
                            "recommendation": "Disable XML-RPC via web server rules (block access to /xmlrpc.php) or use a security plugin if Jetpack or mobile app sync is not required."
                        })
                except Exception:
                    pass

            elif detected_cms == "Joomla":
                admin_url = f"{origin}/administrator/"
                try:
                    probe_admin = await client.get(admin_url, timeout=3.0)
                    is_admin_active = probe_admin.status_code in [200, 303]
                    login_path_probe = {
                        "tested_path": "/administrator/",
                        "accessible": is_admin_active,
                        "status_code": probe_admin.status_code,
                        "redirected": probe_admin.status_code == 303
                    }
                    if is_admin_active:
                        login_path_detected = f"{admin_url} (HTTP {probe_admin.status_code})"
                        findings.append({
                            "finding_key": "cms.joomla.admin_exposed",
                            "title": "Joomla Administrator Portal Publicly Accessible",
                            "severity": "low",
                            "confidence": "high",
                            "category": "CMS Exposure",
                            "evidence": f"Joomla administrative endpoint '{admin_url}' returned HTTP {probe_admin.status_code}.",
                            "recommendation": "Enforce two-factor authentication or restrict /administrator/ access by IP address."
                        })
                except Exception:
                    pass

            elif detected_cms == "Drupal":
                drupal_login = f"{origin}/user/login"
                try:
                    probe_drupal = await client.get(drupal_login, timeout=3.0)
                    login_path_probe = {
                        "tested_path": "/user/login",
                        "accessible": probe_drupal.status_code == 200,
                        "status_code": probe_drupal.status_code,
                        "redirected": False
                    }
                    if probe_drupal.status_code == 200:
                        login_path_detected = f"{drupal_login} (HTTP 200)"
                except Exception:
                    pass

        # -------------------------------------------------------------
        # 6. Version Disclosure Finding or Passed Check
        # -------------------------------------------------------------
        if cms_version and detected_cms:
            findings.append({
                "finding_key": f"cms.{detected_cms.lower()}.version_disclosure",
                "title": f"Public {detected_cms} Version Disclosure",
                "severity": "medium",
                "confidence": "high",
                "category": "Information Disclosure",
                "evidence": f"HTML source explicitly advertises '{detected_cms} {cms_version}' in meta generator tag: '{generator_content}'. Attackers query version numbers against known CVE databases.",
                "recommendation": f"Remove or mask the generator meta tag in your {detected_cms} theme settings or via security headers."
            })
        elif detected_cms:
            passed_checks.append(f"CMS detected ({detected_cms}) without public version leakage in generator tags")

        if detected_plugins:
            findings.append({
                "finding_key": "cms.plugins.leakage",
                "title": f"Visible CMS Plugin Identifiers ({len(detected_plugins)} found)",
                "severity": "low",
                "confidence": "medium",
                "category": "Reconnaissance Exposure",
                "evidence": f"HTML source links reference specific plugin assets: {', '.join(detected_plugins[:5])}.",
                "recommendation": "Keep all installed plugins updated to their latest patches, and remove unused extensions to minimize attack surface."
            })

        if not detected_cms:
            passed_checks.append("Zero common CMS footprint signatures exposed in root HTML markup")

        # Deduplicate technologies list
        all_techs = []
        if detected_cms:
            all_techs.append(detected_cms)
        for s in signatures_observed:
            clean_s = s.split(":")[0].strip() if ":" in s else s
            if "Generator" not in clean_s and clean_s not in all_techs:
                all_techs.append(clean_s)
        for lib in libraries_detected:
            if lib not in all_techs:
                all_techs.append(lib)

        cms_details: Dict[str, Any] = {
            "detected": detected_cms is not None,
            "cms_detected": detected_cms is not None,
            "detected_cms": detected_cms or "Custom / Jamstack",
            "cms_name": detected_cms or "Custom / Jamstack",
            "platform_type": platform_type,
            "version": cms_version or "Not publicly disclosed",
            "cms_version": cms_version,
            "web_server": web_server,
            "backend_runtime": backend_runtime,
            "runtime": backend_runtime,
            "signatures": signatures_observed,
            "technologies": all_techs,
            "plugins": detected_plugins,
            "themes": detected_themes,
            "theme": detected_themes[0] if detected_themes else None,
            "libraries": libraries_detected,
            "login_path": login_path_detected or "Not observed on standard paths",
            "login_path_probe": login_path_probe,
            "xmlrpc_active": xmlrpc_detected,
            "xmlrpc_probe": xmlrpc_probe,
            "technology_profile": tech_profile
        }

        return cms_details, findings, passed_checks

cms_fingerprinter = CmsFingerprinter()

def fingerprint_cms_static(html_text: str, response_headers: Dict[str, str], origin: str = "") -> Dict[str, Any]:
    """
    Synchronous helper for static CMS fingerprinting without network probes.
    """
    import asyncio
    details, _, _ = asyncio.run(cms_fingerprinter.inspect_cms(html_text, response_headers, None, origin))
    return details
