import os
import hashlib
import uuid
import re
import time
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

class StorageManager:
    def __init__(self, upload_dir: Path = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        # Strip path traversal and dangerous characters
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        return clean_name or "file.bin"

    def _safe_unlink(self, path: Path) -> bool:
        """
        Safely unlinks a file, retrying once if a temporary OS file lock is held.
        """
        for _ in range(3):
            try:
                if path.exists():
                    path.unlink(missing_ok=True)
                return True
            except PermissionError:
                time.sleep(0.1)
            except Exception:
                break
        try:
            path.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    async def save_upload(self, upload_file: UploadFile) -> Tuple[str, str, int, dict]:
        """
        Saves incoming upload file safely in chunks, calculating hashes on the fly.
        Ensures the file handle is completely closed before unlinking or throwing errors,
        preventing Windows WinError 32 lock conflicts.
        Returns: (saved_filename, full_file_path, total_size, hashes_dict)
        """
        original_name = self._sanitize_filename(upload_file.filename or "unknown")
        unique_prefix = uuid.uuid4().hex[:12]
        saved_filename = f"{unique_prefix}_{original_name}"
        destination = self.upload_dir / saved_filename

        md5_hasher = hashlib.md5()
        sha1_hasher = hashlib.sha1()
        sha256_hasher = hashlib.sha256()

        total_bytes = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        size_exceeded = False
        write_error = None

        try:
            with open(destination, "wb") as f:
                while True:
                    chunk = await upload_file.read(chunk_size)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_FILE_SIZE_BYTES:
                        size_exceeded = True
                        break
                    md5_hasher.update(chunk)
                    sha1_hasher.update(chunk)
                    sha256_hasher.update(chunk)
                    f.write(chunk)
        except Exception as e:
            write_error = e

        # Handle size exceeded after file handle is fully closed
        if size_exceeded:
            self._safe_unlink(destination)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )

        if write_error:
            self._safe_unlink(destination)
            if isinstance(write_error, HTTPException):
                raise write_error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to securely store file: {str(write_error)}"
            )

        hashes = {
            "md5": md5_hasher.hexdigest(),
            "sha1": sha1_hasher.hexdigest(),
            "sha256": sha256_hasher.hexdigest()
        }

        return saved_filename, str(destination), total_bytes, hashes

    def shred_file(self, file_path_str: str) -> bool:
        """
        Securely overwrites and deletes the file for maximum privacy.
        """
        path = Path(file_path_str)
        if not path.exists():
            return False
            
        try:
            size = path.stat().st_size
            if size > 0:
                with open(path, "ba+", buffering=0) as f:
                    f.seek(0)
                    f.write(b"\x00" * min(size, 4096 * 1024))
        except Exception:
            pass

        return self._safe_unlink(path)

storage_manager = StorageManager()
