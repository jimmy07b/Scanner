import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.models import ScanResult, Finding
from app.services.url_checker import url_checker
from app.services.website_auditor import website_auditor
from app.services.file_scanner import file_scanner
from app.services.report_builder import report_builder
from app.services.risk_engine import risk_engine

class ScanQueue:
    """
    Asynchronous Scan Job Pipeline & Background Worker.
    Transitions scan jobs across stages:
    queued (0%) -> fetching (25%) -> analyzing (50%) -> extracting (75%) -> scoring (90%) -> completed (100%)
    and failed for errors/timeouts.
    """

    async def create_job(
        self,
        scan_type: str,
        target_name: str,
        upload_id: Optional[str] = None,
        file_path: Optional[str] = None,
        hashes: Optional[dict] = None
    ) -> ScanResult:
        """Creates a scan job in queued state and dispatches background worker."""
        async with AsyncSessionLocal() as db:
            job = ScanResult(
                scan_type=scan_type,
                target_name=target_name,
                status="queued",
                stage="queued",
                progress=0,
                verdict="evaluating",
                summary="Scan queued for background analysis...",
                raw_metadata={"stage": "queued", "progress": 0, "target": target_name},
                upload_id=upload_id
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            job_id = job.id

        # Launch background worker task asynchronously
        asyncio.create_task(
            self._execute_worker(
                scan_id=job_id,
                scan_type=scan_type,
                target_name=target_name,
                file_path=file_path,
                hashes=hashes
            )
        )

        return job

    async def _update_stage(self, scan_id: str, stage: str, progress: int, status: str = "running"):
        async with AsyncSessionLocal() as db:
            stmt = (
                update(ScanResult)
                .where(ScanResult.id == scan_id)
                .values(stage=stage, progress=progress, status=status)
            )
            await db.execute(stmt)
            await db.commit()

    async def _execute_worker(
        self,
        scan_id: str,
        scan_type: str,
        target_name: str,
        file_path: Optional[str] = None,
        hashes: Optional[dict] = None
    ):
        try:
            # Stage 1: Fetching
            await self._update_stage(scan_id, stage="fetching", progress=20, status="running")
            await asyncio.sleep(0.2)

            # Stage 2: Passive & Bounded Active Recon
            await self._update_stage(scan_id, stage="recon", progress=40, status="running")
            await asyncio.sleep(0.2)

            # Stage 3: Security Analysis
            await self._update_stage(scan_id, stage="analyzing", progress=65, status="running")

            # Execute the relevant engine
            findings_raw = []
            passed_checks = []
            collected_data = {}
            verdict = "safe"
            risk_score = 0
            status_label = "clean"
            summary = ""

            if scan_type in ["url_check", "url"]:
                risk_score, status_label, verdict, summary, findings_raw, passed_checks, collected_data = (
                    await url_checker.check_url(target_name)
                )
            elif scan_type in ["website", "website_audit"]:
                risk_score, status_label, verdict, summary, findings_raw, passed_checks, collected_data = (
                    await website_auditor.audit_website(target_name)
                )
            elif scan_type == "file":
                if not file_path:
                    raise ValueError(f"No file path provided for file scan {scan_id}")
                risk_score, status_label, summary, findings_raw, raw_meta = file_scanner.scan_file(
                    file_path=file_path,
                    original_filename=target_name,
                    hashes=hashes or {}
                )
                verdict = raw_meta.get("verdict", status_label)
                passed_checks = raw_meta.get("passed_checks", [])
                collected_data = raw_meta.get("collected_data", {})

            # Stage 4: Extracting Evidence
            await self._update_stage(scan_id, stage="extracting", progress=80, status="running")
            await asyncio.sleep(0.15)

            # Stage 5: Scoring Risk & Report Assembly
            await self._update_stage(scan_id, stage="scoring", progress=95, status="running")

            # Build final verified report
            final_report = report_builder.build_report(
                scan_id=scan_id,
                target=target_name,
                scan_type=scan_type,
                status="completed",
                stage="completed",
                progress=100,
                risk_score=risk_score,
                verdict=verdict,
                findings=findings_raw,
                passed_checks=passed_checks,
                collected_data=collected_data
            )

            # Persist completion and findings to DB
            async with AsyncSessionLocal() as db:
                stmt = select(ScanResult).where(ScanResult.id == scan_id)
                res = await db.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "completed"
                    job.stage = "done"
                    job.progress = 100
                    job.risk_score = risk_score
                    job.verdict = verdict
                    job.summary = final_report["summary"]
                    job.raw_metadata = {
                        **collected_data,
                        "checks": collected_data.get("checks", {}),
                        "passed_checks": passed_checks,
                        "collected_data": collected_data,
                        "verdict": verdict,
                        "evidence_collected": True,
                        "scope_and_method": final_report.get("scope_and_method", {}),
                        "methodology_notes": final_report.get("methodology_notes", {}),
                        "observed_technologies": final_report.get("observed_technologies", {}),
                        "executive_summary": final_report.get("executive_summary", ""),
                    }

                    # Add findings
                    for item in final_report["findings"]:
                        evidence_str = "\n".join(item["evidence"]) if isinstance(item["evidence"], list) else str(item["evidence"])
                        finding = Finding(
                            scan_result_id=job.id,
                            finding_key=item["id"],
                            title=item["title"],
                            severity=item["severity"],
                            confidence=item.get("confidence", "high"),
                            category=item.get("category", "General"),
                            evidence=evidence_str,
                            recommendation=item.get("recommendation")
                        )
                        db.add(finding)

                    await db.commit()

        except Exception as e:
            # Handle failure cleanly without fake data
            async with AsyncSessionLocal() as db:
                stmt = select(ScanResult).where(ScanResult.id == scan_id)
                res = await db.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "failed"
                    job.stage = "failed"
                    job.progress = 100
                    job.verdict = "unreachable"
                    job.summary = f"Scan failed to complete: {str(e)[:180]}"
                    job.raw_metadata = {"error": str(e), "failed": True}
                    await db.commit()


scan_queue = ScanQueue()
