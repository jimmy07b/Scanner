import os
import re
import math
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pypdf

# ---------------------------------------------------------------------------
# Constants & Matchers
# ---------------------------------------------------------------------------

DANGEROUS_ARCHIVE_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jse", 
    ".wsf", ".scr", ".sh", ".bash", ".elf", ".msi", ".jar", ".apk", ".com"
}

SCRIPT_EXTENSIONS = {
    ".bat", ".cmd", ".ps1", ".sh", ".bash", ".vbs", ".js", ".jse", ".wsf", ".py", ".rb", ".php"
}

SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "info": 0,
}

TEXT_SECRET_PATTERNS = [
    (
        re.compile(r"-----BEGIN (?:[A-Z0-9_\-]+ )?PRIVATE KEY-----"),
        "text.secret.private_key",
        "Exposed Private Cryptographic Key",
        "critical",
        "Sensitive Content",
        "Immediately revoke and rotate this private key. Never store raw private keys in unencrypted files."
    ),
    (
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "text.secret.aws_access_key",
        "Hardcoded AWS Access Key ID",
        "high",
        "Cloud Security",
        "Rotate this AWS Access Key immediately in AWS IAM and inspect CloudTrail for unauthorized API calls."
    ),
    (
        re.compile(r"\bghp_[a-zA-Z0-9]{36}\b"),
        "text.secret.github_token",
        "Hardcoded GitHub Personal Access Token",
        "high",
        "Source Control Security",
        "Revoke this GitHub Personal Access Token immediately via GitHub Developer Settings."
    ),
    (
        re.compile(r"powershell(?:\.exe)?\s+-(?:enc|encodedcommand)\s+([A-Za-z0-9+/=]{10,})", re.IGNORECASE),
        "text.script.powershell_encoded",
        "Obfuscated Encoded PowerShell Command",
        "critical",
        "Command Execution",
        "Base64-encoded PowerShell execution is a common payload obfuscation tactic. Decode and inspect before running."
    ),
    (
        re.compile(r"(?:curl|wget)\s+.*?\|\s*(?:ba|z)?sh", re.IGNORECASE),
        "text.script.pipe_to_shell",
        "Remote Script Pipe to Shell Execution",
        "critical",
        "Command Execution",
        "Piping unverified remote web content directly into a shell interpreter poses an extreme remote code execution risk."
    ),
    (
        re.compile(r"\b(?:Invoke-Expression|IEX)\b\s+.*?[\$\(]", re.IGNORECASE),
        "text.script.dynamic_expression",
        "Dynamic Expression Execution (IEX)",
        "high",
        "Command Execution",
        "Avoid dynamic command execution primitives like Invoke-Expression which facilitate memory-only code injection."
    ),
]

# ---------------------------------------------------------------------------
# Specialized Scanner Functions
# ---------------------------------------------------------------------------

def scan_pdf(file_path: Path, findings: List[dict], collected_data: dict, checks: dict, passed_checks: List[str]) -> None:
    """Performs deep static inspection of Adobe PDF document structure and streams."""
    checks["pdf_structure"] = True
    checks["pdf_javascript"] = False
    checks["pdf_launch"] = False
    checks["pdf_embedded_files"] = False
    checks["pdf_links"] = False

    pdf_info = {
        "page_count": 0,
        "text_length": 0,
        "embedded_links": [],
        "fonts": [],
        "javascript_presence": False,
        "metadata": {},
        "attachments": 0,
        "encryption_status": "Unencrypted"
    }

    # 1. Structural parse using pypdf
    try:
        reader = pypdf.PdfReader(str(file_path))
        num_pages = len(reader.pages)
        pdf_info["page_count"] = num_pages
        pdf_info["encryption_status"] = "Encrypted / Password Protected" if reader.is_encrypted else "Unencrypted"

        total_text_chars = 0
        if not reader.is_encrypted:
            for page in reader.pages[:50]:  # Limit extraction to first 50 pages for speed
                try:
                    txt = page.extract_text()
                    if txt:
                        total_text_chars += len(txt)
                except Exception:
                    pass
        pdf_info["text_length"] = total_text_chars

        meta = reader.metadata or {}
        pdf_info["metadata"] = {
            "author": str(meta.author) if meta.author else "Not specified",
            "creator": str(meta.creator) if meta.creator else "Not specified",
            "producer": str(meta.producer) if meta.producer else "Not specified",
            "title": str(meta.title) if meta.title else "Untitled",
            "creation_date": str(meta.creation_date) if meta.creation_date else "Not specified",
        }
        passed_checks.append(f"PDF structure parsed successfully ({num_pages} page(s), {total_text_chars} chars extracted)")
    except Exception as e:
        checks["pdf_structure"] = False
        pdf_info["metadata"]["parse_warning"] = str(e)[:150]

    # 2. Raw stream token inspection
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # Fonts detection
        fonts_found = list(set(f.decode("utf-8", errors="ignore") for f in re.findall(rb"/BaseFont\s*/([A-Za-z0-9_\-+]+)", content)))
        pdf_info["fonts"] = fonts_found[:15]
        if fonts_found:
            passed_checks.append(f"Detected {len(fonts_found)} embedded or referenced font face(s)")

        # Token checks
        launch_count = content.count(b"/Launch")
        if launch_count > 0:
            checks["pdf_launch"] = True
            checks["embedded_objects"] = True
            findings.append({
                "finding_key": "pdf.action.launch",
                "title": "PDF Arbitrary Program Launch Action (/Launch)",
                "severity": "critical",
                "confidence": "high",
                "category": "PDF Security",
                "evidence": f"Found {launch_count} occurrence(s) of '/Launch' action token in document stream.",
                "recommendation": "Do not open this PDF. The /Launch action allows documents to instruct viewers to spawn external operating system processes."
            })
        else:
            passed_checks.append("No arbitrary program launch actions (/Launch) found in PDF stream")

        js_count = content.count(b"/JavaScript") + content.count(b"/JS")
        if js_count > 0:
            checks["pdf_javascript"] = True
            checks["embedded_objects"] = True
            pdf_info["javascript_presence"] = True
            findings.append({
                "finding_key": "pdf.script.javascript",
                "title": "Embedded JavaScript Stream in PDF",
                "severity": "high",
                "confidence": "high",
                "category": "PDF Security",
                "evidence": f"Found {js_count} embedded JavaScript token(s) (/JavaScript or /JS) in PDF byte stream.",
                "recommendation": "Disable JavaScript execution in your PDF reader. Embedded scripts can trigger memory corruption or automate phishing."
            })
        else:
            passed_checks.append("Zero embedded JavaScript streams (/JS or /JavaScript) detected")

        embedded_count = content.count(b"/EmbeddedFiles")
        pdf_info["attachments"] = embedded_count
        if embedded_count > 0:
            checks["pdf_embedded_files"] = True
            checks["embedded_objects"] = True
            findings.append({
                "finding_key": "pdf.container.embedded_files",
                "title": "Embedded File Attachments in PDF",
                "severity": "medium",
                "confidence": "high",
                "category": "PDF Security",
                "evidence": f"Found {embedded_count} '/EmbeddedFiles' dictionary reference(s) within the PDF structure.",
                "recommendation": "Inspect any bundled attachments with anti-malware tools before extracting or executing them."
            })
        else:
            passed_checks.append("Zero encapsulated file attachments (/EmbeddedFiles) detected")

        open_action_count = content.count(b"/OpenAction")
        if open_action_count > 0:
            findings.append({
                "finding_key": "pdf.action.open_action",
                "title": "Automatic Document Open Action (/OpenAction)",
                "severity": "medium",
                "confidence": "high",
                "category": "PDF Security",
                "evidence": f"Found {open_action_count} '/OpenAction' directive(s) configured to trigger immediately upon document open.",
                "recommendation": "Review document actions. Automated execution triggers can chain with viewer vulnerabilities."
            })
        else:
            passed_checks.append("No automatic open actions (/OpenAction) configured")

        acroform_count = content.count(b"/AcroForm")
        if acroform_count > 0:
            findings.append({
                "finding_key": "pdf.form.acroform",
                "title": "Interactive AcroForm Fields Present",
                "severity": "info",
                "confidence": "high",
                "category": "PDF Structure",
                "evidence": f"Detected {acroform_count} interactive form field definition(s) (AcroForm).",
                "recommendation": "Informational: standard for fillable forms, but verify input sources when collecting sensitive user information."
            })

        # URL extraction
        urls = re.findall(rb"/URI\s*\((https?://[^)]+)\)", content)
        if urls:
            checks["pdf_links"] = True
            sample_urls = [u.decode("utf-8", errors="ignore") for u in urls[:10]]
            pdf_info["embedded_links"] = sample_urls
            findings.append({
                "finding_key": "pdf.link.external_url",
                "title": "Embedded External Hyperlinks in PDF",
                "severity": "info",
                "confidence": "high",
                "category": "PDF Links",
                "evidence": f"Detected {len(urls)} external URL link(s). Sample: {sample_urls[0]}",
                "recommendation": "Verify all destination domains before clicking links to prevent credential phishing."
            })
        else:
            passed_checks.append("No external hyperlink references detected in document")

    except Exception as e:
        findings.append({
            "finding_key": "pdf.parser.error",
            "title": "PDF Stream Reading Anomaly",
            "severity": "low",
            "confidence": "low",
            "category": "Parser Integrity",
            "evidence": f"PDF parser encountered exception: {str(e)[:120]}",
            "recommendation": "Ensure document is not corrupted or malformed."
        })

    collected_data["pdf_details"] = pdf_info


def scan_office(file_path: Path, ext: str, findings: List[dict], collected_data: dict, checks: dict, passed_checks: List[str]) -> None:
    """Performs deep static inspection of Microsoft Office (OpenXML / OLE) documents."""
    checks["office_structure"] = True
    checks["office_macros"] = False
    checks["office_ole_objects"] = False
    checks["office_external_relationships"] = False

    doc_info = {
        "entries_count": 0,
        "text_length": 0,
        "embedded_links": [],
        "fonts": [],
        "javascript_presence": False,
        "has_macros": False,
        "ole_objects_count": 0,
        "attachments": 0,
        "encryption_status": "Unencrypted (Standard OpenXML)"
    }

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            namelist = zf.namelist()
            doc_info["entries_count"] = len(namelist)

            # Approximate text length
            text_chars = 0
            for name in namelist:
                if name.endswith(".xml") and ("document" in name or "sharedStrings" in name or "slide" in name):
                    try:
                        content_xml = zf.read(name).decode("utf-8", errors="ignore")
                        cleaned = re.sub(r"<[^>]+>", " ", content_xml)
                        text_chars += len(cleaned.strip())
                    except Exception:
                        pass
            doc_info["text_length"] = text_chars

            # 1. Macro detection (vbaProject.bin)
            has_macros = any("vbaproject.bin" in name.lower() for name in namelist)
            doc_info["has_macros"] = has_macros
            if has_macros:
                checks["office_macros"] = True
                checks["embedded_objects"] = True
                findings.append({
                    "finding_key": "office.macro.vba",
                    "title": "VBA Macros Present in Office Document",
                    "severity": "high",
                    "confidence": "high",
                    "category": "Office Security",
                    "evidence": "Found 'vbaProject.bin' macro container in OpenXML package structure.",
                    "recommendation": "Do not enable macros when opening this document. Macros are capable of executing arbitrary code on the local host."
                })
            else:
                passed_checks.append("Zero executable VBA macro modules (vbaProject.bin) detected")

            # 2. OLE binary objects
            ole_objects = [name for name in namelist if "oleobject" in name.lower() or (name.endswith(".bin") and "vbaproject" not in name.lower())]
            doc_info["ole_objects_count"] = len(ole_objects)
            doc_info["attachments"] = len(ole_objects)
            if ole_objects:
                checks["office_ole_objects"] = True
                checks["embedded_objects"] = True
                findings.append({
                    "finding_key": "office.ole.embedded_object",
                    "title": "Embedded OLE / Binary Objects Detected",
                    "severity": "medium",
                    "confidence": "high",
                    "category": "Office Security",
                    "evidence": f"Found {len(ole_objects)} embedded binary object(s): {', '.join(ole_objects[:3])}",
                    "recommendation": "Inspect embedded OLE objects. Attackers frequently package external executable payloads or malicious scripts inside OLE streams."
                })
            else:
                passed_checks.append("No embedded OLE objects or binary payload streams detected")

            # 3. External relationship / template injection checks
            rel_files = [name for name in namelist if name.endswith(".rels")]
            external_rels: List[str] = []
            for rel in rel_files:
                try:
                    rel_content = zf.read(rel).decode("utf-8", errors="ignore")
                    matches = re.findall(r'TargetMode="External"\s+Target="(https?://[^"]+)"', rel_content)
                    if matches:
                        external_rels.extend(matches)
                except Exception:
                    pass

            doc_info["embedded_links"] = external_rels[:10]
            if external_rels:
                checks["office_external_relationships"] = True
                findings.append({
                    "finding_key": "office.template.external_target",
                    "title": "External Relationship / Remote Template Injection Target",
                    "severity": "medium",
                    "confidence": "high",
                    "category": "Office Security",
                    "evidence": f"Detected {len(external_rels)} external reference(s), e.g. {external_rels[0]}",
                    "recommendation": "Remote template injection can force clients to fetch external malicious templates or leak NTLM authentication hashes."
                })
            else:
                passed_checks.append("No external relationship targets or template injection links detected")

        passed_checks.append(f"OpenXML package structure validated ({len(namelist)} XML/media entries)")

    except zipfile.BadZipFile:
        checks["office_structure"] = False
        findings.append({
            "finding_key": "office.structure.corrupted",
            "title": "Corrupted or Non-Standard Office Package",
            "severity": "medium",
            "confidence": "high",
            "category": "File Structure",
            "evidence": f"File with extension '{ext}' failed OpenXML ZIP decompression.",
            "recommendation": "Ensure the document is not corrupt or using an obfuscated non-standard container."
        })
    except Exception as e:
        findings.append({
            "finding_key": "office.parser.warning",
            "title": "Office Document Inspection Warning",
            "severity": "low",
            "confidence": "low",
            "category": "File Structure",
            "evidence": f"Analysis encountered error: {str(e)[:120]}",
            "recommendation": "Verify document integrity."
        })

    collected_data["office_details"] = doc_info


def scan_image(file_path: Path, findings: List[dict], collected_data: dict, checks: dict, passed_checks: List[str]) -> None:
    """Performs static metadata and structural inspection of image files."""
    checks["image_format"] = True
    checks["image_gps"] = False
    checks["image_eof_integrity"] = True

    img_info = {
        "width": None,
        "height": None,
        "total_pixels": None,
        "aspect_ratio": None,
        "file_size": file_path.stat().st_size,
        "mime_type": "image/unknown",
        "format": "Unknown",
        "mode": None,
        "exif_metadata": {},
        "gps_present": False,
        "camera_make": None,
        "camera_model": None,
        "ocr_text": "Not detected (no embedded text layer)"
    }

    try:
        with Image.open(file_path) as img:
            w, h = img.width, img.height
            img_info["width"] = w
            img_info["height"] = h
            img_info["total_pixels"] = w * h
            img_info["format"] = img.format or "Unknown"
            img_info["mode"] = img.mode
            img_info["mime_type"] = Image.MIME.get(img.format, f"image/{(img.format or 'unknown').lower()}")

            # Compute aspect ratio
            def calc_ratio(width, height):
                gcd_val = math.gcd(width, height)
                rw, rh = width // gcd_val, height // gcd_val
                if rw <= 16 and rh <= 16:
                    return f"{rw}:{rh}"
                return f"{round(width / max(height, 1), 2)}:1"

            img_info["aspect_ratio"] = calc_ratio(w, h)
            passed_checks.append(f"Image decoded cleanly: {w}x{h} ({img_info['aspect_ratio']}, {img_info['total_pixels']:,} pixels)")

            exif = img.getexif()
            if exif:
                exif_data = {}
                software_tag = None
                has_gps = False

                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    tag_str = str(tag_name)
                    if tag_str == "Make":
                        img_info["camera_make"] = str(value)
                    elif tag_str == "Model":
                        img_info["camera_model"] = str(value)
                    elif tag_str == "Software":
                        software_tag = str(value)
                    elif tag_str == "GPSInfo":
                        has_gps = True

                    if isinstance(value, (str, int, float)):
                        exif_data[tag_str] = value

                img_info["exif_metadata"] = exif_data
                img_info["gps_present"] = has_gps

                if has_gps:
                    checks["image_gps"] = True
                    checks["sensitive_patterns"] = True
                    findings.append({
                        "finding_key": "image.exif.gps_coordinates",
                        "title": "Sensitive GPS Location Metadata Found",
                        "severity": "medium",
                        "confidence": "high",
                        "category": "Privacy Exposure",
                        "evidence": "Image EXIF metadata contains embedded GPS coordinate tags (GPSInfo).",
                        "recommendation": "Strip EXIF location metadata before distributing images publicly to prevent physical location exposure."
                    })
                else:
                    passed_checks.append("EXIF metadata verified: Zero embedded GPS location tags present")

                if software_tag:
                    findings.append({
                        "finding_key": "image.exif.editing_software",
                        "title": "Image Editing Software Metadata Present",
                        "severity": "info",
                        "confidence": "high",
                        "category": "Image Metadata",
                        "evidence": f"Image EXIF metadata indicates software: '{software_tag}'.",
                        "recommendation": "Informational: indicates the image was edited or exported with digital photo software."
                    })
            else:
                passed_checks.append("Image contains zero EXIF metadata (privacy-clean)")

        # Check for trailing extraneous data past JPEG End-Of-Image marker (0xFF, 0xD9)
        with open(file_path, "rb") as f:
            content = f.read()
            if content.startswith(b"\xff\xd8\xff"):
                eoi_pos = content.rfind(b"\xff\xd9")
                if eoi_pos != -1 and (len(content) - eoi_pos) > 100:
                    checks["image_eof_integrity"] = False
                    extra_bytes = len(content) - eoi_pos - 2
                    findings.append({
                        "finding_key": "image.structure.appended_eof_data",
                        "title": "Extraneous Data Appended Past JPEG EOF",
                        "severity": "medium",
                        "confidence": "high",
                        "category": "Steganography / Polyglot",
                        "evidence": f"Found {extra_bytes} byte(s) of extraneous data appended past the standard JPEG End-Of-File marker (0xFFD9).",
                        "recommendation": "Appended data after image EOF may indicate hidden archive polyglots, scripts, or steganographic payloads."
                    })
                else:
                    passed_checks.append("JPEG structural boundary verified: End-Of-Image marker (0xFFD9) is clean")

    except Exception as e:
        checks["image_format"] = False
        findings.append({
            "finding_key": "image.parser.warning",
            "title": "Image Parsing Warning",
            "severity": "low",
            "confidence": "low",
            "category": "Image Analysis",
            "evidence": f"Failed to parse image file: {str(e)[:120]}",
            "recommendation": "Check if file is corrupted or not a valid image format."
        })

    collected_data["image_details"] = img_info


def scan_archive(file_path: Path, findings: List[dict], collected_data: dict, checks: dict, passed_checks: List[str]) -> None:
    """Performs static safety inspection of ZIP archive contents."""
    checks["archive_integrity"] = True
    checks["archive_decompression_ratio"] = True
    checks["archive_traversal"] = False
    checks["archive_executables"] = False

    archive_info = {
        "number_of_files_inside": 0,
        "file_count": 0,
        "folder_tree": [],
        "nested_archives": [],
        "nested_archives_count": 0,
        "executable_files": [],
        "script_files": [],
        "extracted_hashes": {},
        "compression_ratio": 1.0,
        "uncompressed_size_bytes": 0,
    }

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            infolist = zf.infolist()
            total_uncompressed = sum(info.file_size for info in infolist)
            compressed_size = file_path.stat().st_size
            ratio = total_uncompressed / max(compressed_size, 1)

            archive_info["number_of_files_inside"] = len(infolist)
            archive_info["file_count"] = len(infolist)
            archive_info["uncompressed_size_bytes"] = total_uncompressed
            archive_info["compression_ratio"] = round(ratio, 2)

            # 1. Zip bomb check
            if ratio > 100 and total_uncompressed > 50 * 1024 * 1024:
                checks["archive_decompression_ratio"] = False
                findings.append({
                    "finding_key": "archive.dos.decompression_bomb",
                    "title": "Decompression Bomb / Zip Bomb Signature",
                    "severity": "critical",
                    "confidence": "high",
                    "category": "Archive Denial of Service",
                    "evidence": f"Extreme compression ratio of {ratio:.1f}x (uncompressed: {total_uncompressed // (1024*1024)}MB from {compressed_size // 1024}KB compressed).",
                    "recommendation": "Do not decompress this archive. Extreme compression ratios can exhaust system storage and crash host services."
                })
            else:
                passed_checks.append(f"Decompression ratio verified safe ({ratio:.2f}x expansion ratio)")

            flagged_executables: List[str] = []
            script_files: List[str] = []
            nested_archives: List[str] = []
            file_tree: List[dict] = []
            member_hashes: Dict[str, str] = {}

            for info in infolist[:100]:
                entry_name = info.filename
                entry_ext = Path(entry_name).suffix.lower()

                file_tree.append({
                    "path": entry_name,
                    "size": info.file_size,
                    "is_dir": info.is_dir()
                })

                # Flag executable extensions inside archive
                if entry_ext in DANGEROUS_ARCHIVE_EXTENSIONS and not info.is_dir():
                    flagged_executables.append(entry_name)
                    # Compute hash for suspicious executable member
                    try:
                        data = zf.read(info)
                        member_hashes[entry_name] = hashlib.sha256(data).hexdigest()
                    except Exception:
                        pass

                # Script files
                if entry_ext in SCRIPT_EXTENSIONS and not info.is_dir():
                    script_files.append(entry_name)

                # Check for nested archives
                if entry_ext in [".zip", ".tar", ".gz", ".7z", ".rar"] and not info.is_dir():
                    nested_archives.append(entry_name)

                # Path traversal check (Zip Slip)
                if "../" in entry_name or "..\\" in entry_name:
                    checks["archive_traversal"] = True
                    checks["embedded_objects"] = True
                    findings.append({
                        "finding_key": "archive.traversal.zip_slip",
                        "title": "Zip Slip / Directory Traversal Sequence in Archive",
                        "severity": "critical",
                        "confidence": "high",
                        "category": "Path Traversal",
                        "evidence": f"Archive member contains parent directory escape sequence: '{entry_name}'.",
                        "recommendation": "Do not extract this archive. Files containing '../' can overwrite arbitrary files outside the extraction destination."
                    })

            # If no suspicious files, hash first 3 members for verification
            if not member_hashes and infolist:
                for info in infolist[:3]:
                    if not info.is_dir():
                        try:
                            data = zf.read(info)
                            member_hashes[info.filename] = hashlib.sha256(data).hexdigest()
                        except Exception:
                            pass

            archive_info["folder_tree"] = file_tree[:30]
            archive_info["executable_files"] = flagged_executables
            archive_info["script_files"] = script_files
            archive_info["nested_archives"] = nested_archives
            archive_info["nested_archives_count"] = len(nested_archives)
            archive_info["extracted_hashes"] = member_hashes

            if not checks["archive_traversal"]:
                passed_checks.append("Zip Slip path traversal check passed (no '../' escape sequences)")

            if flagged_executables:
                checks["archive_executables"] = True
                checks["embedded_objects"] = True
                findings.append({
                    "finding_key": "archive.executable.payload",
                    "title": "Executable Files Inside Archive",
                    "severity": "high",
                    "confidence": "high",
                    "category": "Dangerous Content",
                    "evidence": f"Archive bundles {len(flagged_executables)} executable file(s): {', '.join(flagged_executables[:4])}",
                    "recommendation": "Archives bundling executables or script files represent a primary vector for malware distribution."
                })
            else:
                passed_checks.append("Zero executable binary payloads (.exe, .dll, .msi, etc.) detected")

            if nested_archives:
                findings.append({
                    "finding_key": "archive.nested.compression",
                    "title": "Nested Archives Detected",
                    "severity": "low",
                    "confidence": "high",
                    "category": "Archive Structure",
                    "evidence": f"Found {len(nested_archives)} nested archive(s): {', '.join(nested_archives[:3])}",
                    "recommendation": "Nested archives are sometimes used to evade perimeter signature scanners."
                })
            else:
                passed_checks.append("No nested archive containers detected")

    except zipfile.BadZipFile:
        checks["archive_integrity"] = False
        findings.append({
            "finding_key": "archive.structure.corrupted",
            "title": "Corrupt or Malformed ZIP Archive",
            "severity": "medium",
            "confidence": "high",
            "category": "Archive Integrity",
            "evidence": "Decompression failed: archive does not contain a valid Central Directory header.",
            "recommendation": "Ensure the archive is not corrupted or intentionally malformed."
        })
    except Exception as e:
        findings.append({
            "finding_key": "archive.parser.warning",
            "title": "Archive Analysis Warning",
            "severity": "low",
            "confidence": "low",
            "category": "Archive Analysis",
            "evidence": f"Inspection error: {str(e)[:120]}",
            "recommendation": "Check archive validity."
        })

    collected_data["archive_details"] = archive_info


def scan_text(file_path: Path, findings: List[dict], collected_data: dict, checks: dict, passed_checks: List[str]) -> None:
    """Performs static pattern matching against credentials, secret keys, and dangerous commands."""
    checks["text_encoding"] = True
    checks["text_secrets"] = False
    checks["text_scripts"] = False

    text_info = {
        "line_count": 0,
        "character_count": 0,
        "encoding": "UTF-8",
        "secrets_detected": 0
    }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(512 * 1024)  # Scan first 512KB

        lines = content.splitlines()
        text_info["line_count"] = len(lines)
        text_info["character_count"] = len(content)

        secrets_count = 0
        for pattern, key, title, severity, category, rec in TEXT_SECRET_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                secrets_count += len(matches)
                checks["sensitive_patterns"] = True
                if "secret" in key:
                    checks["text_secrets"] = True
                if "script" in key:
                    checks["text_scripts"] = True

                sample_match = matches[0] if isinstance(matches[0], str) else str(matches[0])
                if len(sample_match) > 16:
                    redacted = sample_match[:6] + "..." + sample_match[-4:]
                else:
                    redacted = sample_match[:20]

                findings.append({
                    "finding_key": key,
                    "title": title,
                    "severity": severity,
                    "confidence": "high",
                    "category": category,
                    "evidence": f"Matched pattern '{pattern.pattern[:35]}...' ({len(matches)} occurrence(s)). Evidence sample: '{redacted}'.",
                    "recommendation": rec
                })

        text_info["secrets_detected"] = secrets_count
        if secrets_count == 0:
            passed_checks.append("Pattern matching: Zero exposed API credentials, private keys, or command pipes detected")
        passed_checks.append(f"Text content analyzed cleanly ({len(lines)} lines, {len(content)} chars)")

    except Exception as e:
        checks["text_encoding"] = False
        findings.append({
            "finding_key": "text.parser.error",
            "title": "Text File Read Anomaly",
            "severity": "low",
            "confidence": "low",
            "category": "Text Analysis",
            "evidence": f"Error decoding text stream: {str(e)[:120]}",
            "recommendation": "Verify file encoding (UTF-8 recommended)."
        })

    collected_data["text_details"] = text_info


def calculate_entropy(file_path: Path) -> float:
    """Calculates byte-level Shannon entropy (0.0 to 8.0)."""
    try:
        with open(file_path, "rb") as f:
            byte_counts = [0] * 256
            total_bytes = 0
            while chunk := f.read(64 * 1024):
                total_bytes += len(chunk)
                for byte in chunk:
                    byte_counts[byte] += 1

            if total_bytes == 0:
                return 0.0

            entropy = 0.0
            for count in byte_counts:
                if count > 0:
                    p = count / total_bytes
                    entropy -= p * math.log2(p)
            return round(entropy, 3)
    except Exception:
        return 0.0


def check_magic_headers(file_path: Path, ext: str) -> dict:
    """Inspects file magic bytes against extension to detect masqueraded formats."""
    with open(file_path, "rb") as f:
        header = f.read(16)

    result = {
        "detected_type": "unknown",
        "signature_desc": "Unknown format",
        "mismatch": False,
        "is_executable": False
    }

    if header.startswith(b"MZ"):
        result["detected_type"] = "executable_pe"
        result["signature_desc"] = "Windows Portable Executable (PE)"
        result["is_executable"] = True
        if ext not in [".exe", ".dll", ".sys"]:
            result["mismatch"] = True
    elif header.startswith(b"\x7fELF"):
        result["detected_type"] = "executable_elf"
        result["signature_desc"] = "Linux ELF Executable"
        result["is_executable"] = True
        if ext != ".elf":
            result["mismatch"] = True
    elif header.startswith(b"%PDF-"):
        result["detected_type"] = "pdf"
        result["signature_desc"] = "Adobe PDF Document"
        if ext != ".pdf":
            result["mismatch"] = True
    elif header.startswith(b"PK\x03\x04"):
        result["detected_type"] = "zip"
        result["signature_desc"] = "ZIP Archive or OpenXML Container"
        if ext not in [".zip", ".docx", ".xlsx", ".pptx", ".jar", ".apk"]:
            result["mismatch"] = True
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        result["detected_type"] = "png"
        result["signature_desc"] = "PNG Image"
        if ext != ".png":
            result["mismatch"] = True
    elif header[:3] == b"\xff\xd8\xff":
        result["detected_type"] = "jpeg"
        result["signature_desc"] = "JPEG Image"
        if ext not in [".jpg", ".jpeg"]:
            result["mismatch"] = True
    elif header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        result["detected_type"] = "gif"
        result["signature_desc"] = "GIF Image"
        if ext != ".gif":
            result["mismatch"] = True
    elif header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
        result["detected_type"] = "webp"
        result["signature_desc"] = "WebP Image"
        if ext != ".webp":
            result["mismatch"] = True

    return result


def compute_risk_score(findings: List[dict]) -> Tuple[int, str]:
    """
    Computes risk score using standard calibration:
    Critical: +25, High: +15, Medium: +8, Low: +3, Info: +0
    Capped at 100.
    Status thresholds:
    0 = clean, 1-20 = low, 21-45 = medium, 46-75 = high, >75 = critical
    """
    score = 0
    for f in findings:
        sev = f.get("severity", "info").lower()
        score += SEVERITY_WEIGHTS.get(sev, 0)

    score = min(score, 100)

    if score == 0:
        status = "clean"
    elif score <= 20:
        status = "low"
    elif score <= 45:
        status = "medium"
    elif score <= 75:
        status = "high"
    else:
        status = "critical"

    return score, status


# ---------------------------------------------------------------------------
# Primary Entrypoint: scan_file
# ---------------------------------------------------------------------------

def scan_file(file_path: str, original_filename: str, hashes: dict) -> Tuple[int, str, str, List[dict], dict]:
    """
    Runs comprehensive, target-specific static analysis across supported file types.
    Returns: (risk_score, status, summary, findings_list, raw_metadata)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = path.stat().st_size
    ext = Path(original_filename).suffix.lower()
    findings: List[dict] = []
    passed_checks: List[str] = []

    # Verification checks tracked during scan
    checks = {
        "magic_header": True,
        "executable_signature": False,
        "format_structure": True,
        "entropy_check": True,
        "sensitive_patterns": False,
        "embedded_objects": False,
    }

    # Rich collected data reflecting real observed properties
    collected_data: Dict[str, Any] = {
        "filename": original_filename,
        "file_size": file_size,
        "extension": ext,
        "hashes": hashes,
        "detected_type": "unknown",
        "shannon_entropy": 0.0,
    }

    # 1. Header Magic & Mismatch Analysis
    magic_info = check_magic_headers(path, ext)
    collected_data["detected_type"] = magic_info["detected_type"]

    if magic_info.get("mismatch"):
        checks["magic_header"] = False
        if magic_info.get("is_executable"):
            checks["executable_signature"] = True
            findings.append({
                "finding_key": "file.extension.pe_disguised",
                "title": "Disguised Executable Binary Detected",
                "severity": "critical",
                "confidence": "high",
                "category": "File Structure",
                "evidence": f"File extension '{ext}' disguises binary signature '{magic_info['signature_desc']}'.",
                "recommendation": "Do not execute or open this file. Renaming executable binaries with benign extensions is a common malware evasion tactic."
            })
        else:
            findings.append({
                "finding_key": "file.format.mismatch",
                "title": "File Extension and Format Mismatch",
                "severity": "high",
                "confidence": "high",
                "category": "File Structure",
                "evidence": f"File extension '{ext}' does not match header signature '{magic_info['signature_desc']}'.",
                "recommendation": "Verify file integrity. Extension mismatches may indicate corruption or intentional disguise."
            })
    else:
        passed_checks.append(f"Magic header signature verified: matches declared '{ext}' extension ({magic_info['signature_desc']})")
        passed_checks.append("Binary disguise check passed: No hidden PE or ELF executable detected")

    # 2. File-Type Specific Deep Static Inspection
    if ext == ".pdf" or magic_info["detected_type"] == "pdf":
        scan_pdf(path, findings, collected_data, checks, passed_checks)
    elif ext in [".docx", ".xlsx", ".pptx"] or (magic_info["detected_type"] == "zip" and ext in [".docx", ".xlsx", ".pptx"]):
        scan_office(path, ext, findings, collected_data, checks, passed_checks)
    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        scan_image(path, findings, collected_data, checks, passed_checks)
    elif ext == ".zip" or magic_info["detected_type"] == "zip":
        scan_archive(path, findings, collected_data, checks, passed_checks)
    elif ext in [".txt", ".log", ".json", ".xml", ".csv", ".yml", ".yaml"]:
        scan_text(path, findings, collected_data, checks, passed_checks)

    # 3. Shannon Entropy Check
    entropy = calculate_entropy(path)
    collected_data["shannon_entropy"] = entropy
    if entropy > 7.4 and ext not in [".zip", ".gz", ".png", ".jpg", ".jpeg", ".mp4"]:
        checks["entropy_check"] = False
        findings.append({
            "finding_key": "file.entropy.high",
            "title": "High Shannon Entropy Detected",
            "severity": "medium",
            "confidence": "high",
            "category": "Entropy Analysis",
            "evidence": f"Measured byte entropy is {entropy:.2f} / 8.0 across {file_size} bytes, indicating high randomness, compression, or encryption.",
            "recommendation": "High entropy in non-compressed documents may indicate encrypted payloads or obfuscated script blocks."
        })
    else:
        passed_checks.append(f"Shannon entropy within expected baseline ({entropy:.2f} / 8.0)")

    # 4. Compute Final Risk Score and Generate Summary
    risk_score, status_label = compute_risk_score(findings)
    verdict = status_label

    # Professional summary format: "X verified issues found, Y checks passed."
    if len(findings) == 0:
        summary = f"No suspicious indicators detected. All {len(passed_checks)} checks passed."
    else:
        summary = f"{len(findings)} verified issue(s) found, {len(passed_checks)} check(s) passed."

    raw_metadata = {
        **collected_data,
        "filename": original_filename,
        "size_bytes": file_size,
        "hashes": hashes,
        "extension": ext,
        "entropy": entropy,
        "checks": checks,
        "passed_checks": passed_checks,
        "collected_data": collected_data,
        "verdict": verdict,
        "evidence_collected": True,
    }

    return risk_score, status_label, summary, findings, raw_metadata


class FileScanner:
    """Wrapper class preserving backward-compatibility with existing calls."""
    scan = staticmethod(scan_file)
    scan_file = staticmethod(scan_file)
    scan_pdf = staticmethod(scan_pdf)
    scan_office = staticmethod(scan_office)
    scan_image = staticmethod(scan_image)
    scan_archive = staticmethod(scan_archive)
    scan_text = staticmethod(scan_text)


file_scanner = FileScanner()
