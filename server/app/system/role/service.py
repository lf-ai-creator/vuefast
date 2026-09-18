"""角色管理服务。"""

from datetime import datetime

from loguru import logger
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import SysUserDetails
from app.auth.token import get_token_manager
from app.constants import ROOT_ROLE_CODE
from app.exceptions import BusinessException
from app.pagination import PageResult
from app.response import ResultCode
from app.system.role.constants import DataScopeEnum
from app.system.role.models import SysRole, SysRoleDept, SysRoleMenu
from app.system.role.schemas import RoleCreate, RoleOptionVO, RolePageVO, RoleQuery, RoleUpdate, RoleVO
from app.validation import parse_ids


class RoleService:
    """角色管理：CRUD、菜单分配、数据权限变更踢人。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_management(
        self, actor: SysUserDetails, role_ids: list[int] | None = None, new_code: str | None = None
    ) -> None:
        """普通管理员不能创建、修改或删除超级管理员角色。"""
        if ROOT_ROLE_CODE in actor.roles:
            return
        if new_code == ROOT_ROLE_CODE:
            raise BusinessException(code=ResultCode.ACCESS_DENIED, msg="不能创建或修改超级管理员角色")
        if role_ids:
            protected = await self.db.execute(
                select(SysRole.id).where(
                    SysRole.id.in_(role_ids),
                    SysRole.code == ROOT_ROLE_CODE,
                )
            )
            if protected.scalar() is not None:
                raise BusinessException(code=ResultCode.ACCESS_DENIED, msg="不能管理超级管理员角色")

    async def get_page(self, query: RoleQuery) -> PageResult:
        """分页查询角色列表，支持按名称/编码关键字与状态筛选。"""
        conditions = [SysRole.is_deleted == 0]
        if query.keywords:
            kw = f"%{query.keywords}%"
            conditions.append((SysRole.name.ilike(kw)) | (SysRole.code.ilike(kw)))
        if query.status is not None:
            conditions.append(SysRole.status == query.status)

        base = select(SysRole).where(*conditions)
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0

        offset = (query.pageNum - 1) * query.pageSize
        rows = await self.db.execute(
            select(SysRole).where(*conditions).order_by(SysRole.sort.asc()).offset(offset).limit(query.pageSize)
        )
        roles = rows.scalars().all()
        vo_list = [self._to_page_vo(r) for r in roles]
        return PageResult(records=vo_list, total=total, pageNum=query.pageNum, pageSize=query.pageSize)

    async def get_by_id(self, role_id: int) -> RoleVO:
        """根据 id 获取角色详情（含菜单/部门关联）。"""
        result = await self.db.execute(select(SysRole).where(SysRole.id == role_id, SysRole.is_deleted == 0))
        role = result.scalar_one_or_none()
        if role is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="角色不存在")
        return await self._to_vo(role)

    async def get_options(self) -> list[RoleOptionVO]:
        """返回所有启用角色的下拉选项（id + 名称）。"""
        rows = await self.db.execute(
            select(SysRole.id, SysRole.name).where(SysRole.is_deleted == 0, SysRole.status == 1)
        )
        return [RoleOptionVO(id=r.id, name=r.name) for r in rows]

    async def create(self, form: RoleCreate) -> RoleVO:
        """创建角色并保存其菜单/部门关联；名称或编码重复时返回 B0002。"""
        exist = await self.db.execute(
            select(SysRole.id).where(
                (SysRole.name == form.name) | (SysRole.code == form.code),
                SysRole.is_deleted == 0,
            )
        )
        if exist.scalar() is not None:
            raise BusinessException(code=ResultCode.DUPLICATE_KEY, msg="角色名称或编码已存在")

        role = SysRole(
            name=form.name,
            code=form.code,
            sort=form.sort,
            status=form.status,
            data_scope=form.dataScope,
            create_time=datetime.now(),
        )
        self.db.add(role)
        await self.db.flush()

        await self._save_relations(role.id, form.menuIds, form.deptIds)
        logger.info(f"Role created: {form.code}")
        return await self._to_vo(role)

    async def update(self, form: RoleUpdate) -> RoleVO:
        """更新角色并使关联用户的旧会话失效。"""
        result = await self.db.execute(select(SysRole).where(SysRole.id == form.id, SysRole.is_deleted == 0))
        role = result.scalar_one_or_none()
        if role is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="角色不存在")

        exist = await self.db.execute(
            select(SysRole.id).where(
                (SysRole.name == form.name) | (SysRole.code == form.code),
                SysRole.is_deleted == 0,
                SysRole.id != form.id,
            )
        )
        if exist.scalar() is not None:
            raise BusinessException(code=ResultCode.DUPLICATE_KEY, msg="角色名称或编码已存在")

        role.name = form.name
        role.code = form.code
        role.sort = form.sort
        role.status = form.status
        role.data_scope = form.dataScope
        role.update_time = datetime.now()
        await self.db.flush()

        await self._save_relations(form.id, form.menuIds, form.deptIds)
        logger.info(f"Role updated: {role.code}")

        # 角色或权限变更后重新登录，避免沿用旧角色及数据范围。
        await self._invalidate_role_users_sessions(form.id)

        return await self._to_vo(role)

    async def _invalidate_role_users_sessions(self, role_id: int) -> None:
        """角色数据权限变更后，使关联用户 token 失效。"""
        rows = await self.db.execute(
            text("SELECT user_id FROM sys_user_role WHERE role_id = :rid"),
            {"rid": role_id},
        )
        user_ids = [row.user_id for row in rows]
        if not user_ids:
            return
        token_manager = await get_token_manager()
        for uid in user_ids:
            await token_manager.invalidate_user_sessions(uid)
        logger.info(f"Role data_scope changed, invalidated {len(user_ids)} user sessions for role_id={role_id}")

    async def delete(self, ids: str) -> int:
        """按逗号分隔的 id 列表批量逻辑删除角色。"""
        id_list = parse_ids(ids)
        if not id_list:
            raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="请选择要删除的角色")
        await self.db.execute(text("UPDATE sys_role SET is_deleted = 1 WHERE id = ANY(:ids)"), {"ids": id_list})
        for role_id in id_list:
            await self._invalidate_role_users_sessions(role_id)
        logger.info(f"Roles deleted: {id_list}")
        return len(id_list)

    async def update_status(self, role_id: int, status: int) -> None:
        """启用/禁用角色（status=1 启用，0 禁用）。"""
        result = await self.db.execute(select(SysRole).where(SysRole.id == role_id, SysRole.is_deleted == 0))
        role = result.scalar_one_or_none()
        if role is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="角色不存在")
        role.status = status
        await self.db.flush()
        await self._invalidate_role_users_sessions(role_id)

    async def get_role_form(self, role_id: int) -> RoleUpdate:
        """获取角色编辑表单数据（含已分配菜单/部门 id）。"""
        result = await self.db.execute(select(SysRole).where(SysRole.id == role_id, SysRole.is_deleted == 0))
        role = result.scalar_one_or_none()
        if role is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="角色不存在")
        return await self._to_form(role)

    async def get_role_menu_ids(self, role_id: int) -> list[int]:
        """返回角色关联的菜单 id 列表。"""
        rows = await self.db.execute(select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == role_id))
        return [r for (r,) in rows]

    async def get_role_dept_ids(self, role_id: int) -> list[int]:
        """返回角色关联的数据权限部门 id 列表。"""
        rows = await self.db.execute(select(SysRoleDept.dept_id).where(SysRoleDept.role_id == role_id))
        return [r for (r,) in rows]

    async def assign_menus(self, role_id: int, menu_ids: list[int]) -> None:
        """全量替换角色的菜单关联（先删后插）。"""
        await self.db.execute(text("DELETE FROM sys_role_menu WHERE role_id = :rid"), {"rid": role_id})
        for mid in menu_ids:
            self.db.add(SysRoleMenu(role_id=role_id, menu_id=mid))
        await self.db.flush()
        await self._invalidate_role_users_sessions(role_id)

    async def _save_relations(self, role_id: int, menu_ids: list[int], dept_ids: list[int]) -> None:
        """全量替换角色的菜单与部门关联（先删后插）。"""
        await self.db.execute(text("DELETE FROM sys_role_menu WHERE role_id = :rid"), {"rid": role_id})
        for mid in menu_ids:
            self.db.add(SysRoleMenu(role_id=role_id, menu_id=mid))
        await self.db.execute(text("DELETE FROM sys_role_dept WHERE role_id = :rid"), {"rid": role_id})
        for did in dept_ids:
            self.db.add(SysRoleDept(role_id=role_id, dept_id=did))
        await self.db.flush()

    async def _to_form(self, role: SysRole) -> RoleUpdate:
        menu_ids = await self.get_role_menu_ids(role.id)
        dept_ids = await self.get_role_dept_ids(role.id)
        return RoleUpdate(
            id=role.id,
            name=role.name,
            code=role.code,
            sort=role.sort,
            status=role.status,
            dataScope=role.data_scope,
            menuIds=menu_ids,
            deptIds=dept_ids,
        )

    def _to_page_vo(self, role: SysRole) -> RolePageVO:
        """ORM 对象转分页视图对象，仅含基础字段，不查关联表。"""
        return RolePageVO(
            id=role.id,
            name=role.name,
            code=role.code,
            sort=role.sort,
            status=role.status,
            dataScope=role.data_scope,
            dataScopeLabel=DataScopeEnum.get_label(role.data_scope),
            createTime=str(role.create_time) if role.create_time else None,
            updateTime=str(role.update_time) if role.update_time else None,
        )

    async def _to_vo(self, role: SysRole) -> RoleVO:
        """ORM 对象转详情视图对象，附带菜单/部门关联 id。"""
        menu_ids = await self.get_role_menu_ids(role.id)
        dept_ids = await self.get_role_dept_ids(role.id)
        return RoleVO(
            id=role.id,
            name=role.name,
            code=role.code,
            sort=role.sort,
            status=role.status,
            dataScope=role.data_scope,
            dataScopeLabel=DataScopeEnum.get_label(role.data_scope),
            menuIds=menu_ids,
            deptIds=dept_ids,
            createTime=str(role.create_time) if role.create_time else None,
            updateTime=str(role.update_time) if role.update_time else None,
        )
