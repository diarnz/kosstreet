import asyncio

from sqlalchemy import text

from app.db.engine import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'audit_frames'
                ORDER BY ordinal_position
                """
            )
        )
        print("audit_frames columns:")
        for row in result.all():
            print(" ", row)

        version = await db.execute(text("SELECT version_num FROM alembic_version"))
        print("alembic:", version.scalar())


if __name__ == "__main__":
    asyncio.run(main())
