from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rbac import RoleModel, PermissionModel


async def init_rbac(db: AsyncSession):
    """
    Creates default roles and permissions if they don't exist.
    """
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
        db_perms[perm_name] = perm

    await db.commit()

    admin_role = await get_or_create_role(db, "admin")
    admin_role.permissions = list(db_perms.values())

    user_role = await get_or_create_role(db, "user")
    user_role.permissions = [db_perms["movie:read"]]

    editor_role = await get_or_create_role(db, "editor")
    editor_role.permissions = [
        db_perms["movie:read"],
        db_perms["movie:update"],
        db_perms["movie:create"],
    ]

    await db.commit()
    print("✅ RBAC Initialized: Roles and Permissions Ready.")


async def get_or_create_role(db: AsyncSession, name: str):
    stmt = select(RoleModel).where(RoleModel.name == name)
    result = await db.execute(stmt)
    role = result.scalars().first()
    if not role:
        role = RoleModel(name=name)
        db.add(role)
    return role
