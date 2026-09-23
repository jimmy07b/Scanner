import asyncio
import pytest
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.config import settings
from app.core.security import hash_password
from app.models.models import User
from sqlalchemy import select

async def _init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == settings.ADMIN_DEFAULT_EMAIL)
        res = await db.execute(stmt)
        admin = res.scalars().first()
        if not admin:
            db.add(User(
                email=settings.ADMIN_DEFAULT_EMAIL,
                hashed_password=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                role="admin",
                is_active=True
            ))
            await db.commit()
        else:
            admin.hashed_password = hash_password(settings.ADMIN_DEFAULT_PASSWORD)
            await db.commit()

# Run table initialization once before tests
asyncio.run(_init_tables())
