import asyncio
import logging

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.rbac import RoleModel, PermissionModel
from app.models.user import UserModel  # noqa: F401
from app.models.rating import RatingModel  # noqa: F401
from app.models.watchlist import WatchlistModel  # noqa: F401
from app.models.notification import NotificationModel  # noqa: F401
from app.models.movie import Movie  # noqa: F401


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_rbac():
    async with AsyncSessionLocal() as db:
        logger.info("🌱 Seeding RBAC Permissions...")

        permissions_list = [
            "movie:create",
            "movie:read",
            "movie:update",
            "movie:delete",
            "user:read",
            "user:ban",
            "review:delete",
        ]

        db_perms = {}
        for perm_name in permissions_list:
            stmt = select(PermissionModel).where(PermissionModel.name == perm_name)
            result = await db.execute(stmt)
            perm = result.scalars().first()
            if not perm:
                perm = PermissionModel(name=perm_name)
                db.add(perm)
                logger.info(f"   - Created Permission: {perm_name}")
            else:
                logger.info(f"   - Permission exists: {perm_name}")
            db_perms[perm_name] = perm

        await db.commit()

        admin_role = await get_or_create_role(db, "admin")
        admin_role.permissions = list(db_perms.values())
        logger.info(f"- Assigned {len(admin_role.permissions)} permissions to 'admin'")

        user_role = await get_or_create_role(db, "user")
        user_role.permissions = [db_perms["movie:read"]]
        logger.info(f"- Assigned {len(user_role.permissions)} permissions to 'user'")

        await db.commit()
        logger.info("✅ RBAC Seeding Complete!")


async def get_or_create_role(db, name: str):
    stmt = select(RoleModel).where(RoleModel.name == name)
    result = await db.execute(stmt)
    role = result.scalars().first()
    if not role:
        role = RoleModel(name=name)
        db.add(role)
        logger.info(f"- Created Role: {name}")
    else:
        logger.info(f"- Role exists: {name}")
    return role


if __name__ == "__main__":
    asyncio.run(seed_rbac())
