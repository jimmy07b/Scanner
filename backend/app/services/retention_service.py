from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.models import Upload, FileRetentionJob
from app.core.storage import storage_manager

class RetentionService:
    async def cleanup_expired_files(self, db: AsyncSession) -> dict:
        """
        Finds all files past their retention expiration that have not been shredded,
        securely wipes them from disk, and updates database flags.
        """
        now = datetime.now(timezone.utc)
        stmt = select(Upload).where(
            Upload.retention_expires_at <= now,
            Upload.is_deleted == False
        )
        result = await db.execute(stmt)
        expired_uploads = result.scalars().all()

        deleted_count = 0
        failed_count = 0

        for upload in expired_uploads:
            success = storage_manager.shred_file(upload.file_path)
            upload.is_deleted = True
            
            # Log retention job
            job = FileRetentionJob(
                upload_id=upload.id,
                scheduled_deletion_at=upload.retention_expires_at,
                executed_at=now,
                status="completed" if success else "failed",
                details=f"Auto-purge executed. File shredded: {success}"
            )
            db.add(job)
            if success:
                deleted_count += 1
            else:
                failed_count += 1

        await db.commit()
        return {
            "processed": len(expired_uploads),
            "shredded_successfully": deleted_count,
            "failed": failed_count
        }

    async def shred_upload_immediately(self, upload_id: str, db: AsyncSession) -> bool:
        """
        Allows a user or admin to immediately shred an uploaded file on-demand.
        """
        stmt = select(Upload).where(Upload.id == upload_id)
        result = await db.execute(stmt)
        upload = result.scalars().first()

        if not upload or upload.is_deleted:
            return False

        storage_manager.shred_file(upload.file_path)
        upload.is_deleted = True
        
        job = FileRetentionJob(
            upload_id=upload.id,
            scheduled_deletion_at=upload.retention_expires_at,
            executed_at=datetime.now(timezone.utc),
            status="completed",
            details="Immediate user/admin shred request executed."
        )
        db.add(job)
        await db.commit()
        return True

retention_service = RetentionService()
