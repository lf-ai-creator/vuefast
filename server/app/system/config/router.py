"""系统配置管理。"""

from fastapi import APIRouter, Depends, Query, Request
from datetime import datetime
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import SysUserDetails
from app.serializers import BigId
from loguru import logger

from app.pagination import PageResult
from app.database import get_db
from app.redis import get_redis
from app.dependencies import get_current_user, require_perm
from app.exceptions import BusinessException
from app.response import Result, ResultCode
from app.system.config.models import SysConfig
from app.system.log.constants import ActionTypeEnum, LogModuleEnum
from app.system.log.operation_log import operation_log

router = APIRouter(prefix="/api/v1/configs", tags=["系统配置"])


class ConfigQuery(BaseModel):
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    keywords: str | None = None


class ConfigForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: BigId | None = None
    configName: str = Field(..., min_length=1, max_length=50, validation_alias=AliasChoices("configName", "config_name"))
    configKey: str = Field(..., min_length=1, max_length=50, validation_alias=AliasChoices("configKey", "config_key"))
    configValue: str = Field(..., min_length=1, max_length=100, validation_alias=AliasChoices("configValue", "config_value"))
    remark: str | None = Field(default=None, max_length=255)


class ConfigVO(ConfigForm):
    createTime: datetime | None = Field(default=None, validation_alias=AliasChoices("createTime", "create_time"))
    updateTime: datetime | None = Field(default=None, validation_alias=AliasChoices("updateTime", "update_time"))

    @field_serializer("createTime", "updateTime")
    def serialize_time(self, value: datetime | None) -> str | None:
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


class ConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_page(self, query: ConfigQuery) -> PageResult:
        """分页查询系统配置，支持按名称/键关键字筛选。"""
        conditions = [SysConfig.is_deleted == 0]
        if query.keywords:
            kw = f"%{query.keywords}%"
            conditions.append(SysConfig.config_name.ilike(kw) | SysConfig.config_key.ilike(kw))
        base = select(SysConfig).where(*conditions)
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
        offset = (query.pageNum - 1) * query.pageSize
        rows = await self.db.execute(
            select(SysConfig).where(*conditions).order_by(SysConfig.id.desc()).offset(offset).limit(query.pageSize)
        )
        vo_list = [ConfigVO.model_validate(r, from_attributes=True) for r in rows.scalars().all()]
        return PageResult(records=vo_list, total=total, pageNum=query.pageNum, pageSize=query.pageSize)

    async def get_config_form(self, config_id: int) -> ConfigForm:
        """获取配置编辑表单数据。"""
        obj = await self.db.get(SysConfig, config_id)
        if obj is None or obj.is_deleted:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="配置不存在")
        return ConfigForm.model_validate(obj, from_attributes=True)

    async def get_by_key(self, key: str) -> str | None:
        """按 config_key 读取配置值；未命中返回 None。"""
        r = await self.db.execute(select(SysConfig.config_value).where(SysConfig.config_key == key, SysConfig.is_deleted == 0))
        return r.scalar()

    async def create(self, form: ConfigForm) -> ConfigVO:
        """创建配置；config_key 重复时返回 B0002。"""
        exist = await self.db.execute(select(SysConfig.id).where(SysConfig.config_key == form.configKey))
        if exist.scalar() is not None:
            raise BusinessException(code=ResultCode.DUPLICATE_KEY, msg="配置键已存在")
        obj = SysConfig(config_name=form.configName, config_key=form.configKey, config_value=form.configValue, remark=form.remark)
        self.db.add(obj)
        await self.db.flush()
        return ConfigVO.model_validate(obj, from_attributes=True)

    async def update(self, config_id: int, form: ConfigForm) -> ConfigVO:
        """更新配置；config_key 重复时返回 B0002。"""
        obj = await self.db.get(SysConfig, config_id)
        if obj is None or obj.is_deleted:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="配置不存在")
        exist = await self.db.execute(select(SysConfig.id).where(SysConfig.config_key == form.configKey, SysConfig.id != config_id))
        if exist.scalar() is not None:
            raise BusinessException(code=ResultCode.DUPLICATE_KEY, msg="配置键已存在")
        obj.config_name = form.configName
        obj.config_key = form.configKey
        obj.config_value = form.configValue
        obj.remark = form.remark
        await self.db.flush()
        await self.db.refresh(obj)
        await self.db.refresh(obj)
        return ConfigVO.model_validate(obj, from_attributes=True)

    async def delete(self, ids: str) -> int:
        """批量逻辑删除配置（逗号分隔 id）。"""
        try:
            id_list = list(dict.fromkeys(int(x) for x in ids.split(",") if x.strip()))
        except ValueError:
            raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="配置 ID 格式错误")
        if not id_list:
            raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="请选择要删除的配置")
        count = 0
        for cid in id_list:
            obj = await self.db.get(SysConfig, cid)
            if obj and not obj.is_deleted:
                obj.is_deleted = 1
                count += 1
        await self.db.flush()
        return count

    async def refresh_cache(self) -> bool:
        """将所有启用配置写入 Redis（key=config:{config_key}），供运行时读取。"""
        redis = await get_redis()
        rows = await self.db.execute(select(SysConfig.config_key, SysConfig.config_value, SysConfig.is_deleted))
        configs = rows.all()
        registry = "config:cache:__managed_keys__"
        previous_keys = {
            key.decode() if isinstance(key, bytes) else key for key in await redis.smembers(registry)
        }
        active = {f"config:{key}": value or "" for key, value, deleted in configs if not deleted}
        deleted_keys = {f"config:{key}" for key, _, deleted in configs if deleted}
        stale_keys = (previous_keys | deleted_keys) - active.keys()
        async with redis.pipeline(transaction=True) as pipeline:
            if stale_keys:
                pipeline.delete(*sorted(stale_keys))
            for key, value in active.items():
                pipeline.set(key, value)
            pipeline.delete(registry)
            if active:
                pipeline.sadd(registry, *sorted(active))
            await pipeline.execute()
        logger.info("Config cache refreshed")
        return True


@router.get("", summary="配置分页", dependencies=[Depends(require_perm("sys:config:list"))])
async def get_configs(
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keywords: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return Result(data=await ConfigService(db).get_page(ConfigQuery(pageNum=pageNum, pageSize=pageSize, keywords=keywords)))


@router.get("/{config_id}/form", summary="配置表单数据", dependencies=[Depends(require_perm("sys:config:update"))])
async def get_config_form(config_id: int, db: AsyncSession = Depends(get_db)):
    return Result(data=await ConfigService(db).get_config_form(config_id))


@router.get("/{config_key}/value", summary="根据key获取配置值")
async def get_config_value(config_key: str, db: AsyncSession = Depends(get_db)):
    return Result(data=await ConfigService(db).get_by_key(config_key))


@router.put("/refresh", summary="刷新配置缓存", dependencies=[Depends(require_perm("sys:config:refresh"))])
@operation_log(module=LogModuleEnum.CONFIG, action_type=ActionTypeEnum.UPDATE, title="刷新配置缓存")
async def refresh_config_cache(
    request: Request, user: SysUserDetails = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    return Result(data=await ConfigService(db).refresh_cache())


@router.post("", summary="创建配置", dependencies=[Depends(require_perm("sys:config:create"))])
@operation_log(module=LogModuleEnum.CONFIG, action_type=ActionTypeEnum.INSERT, title="新增配置")
async def create_config(
    request: Request, form: ConfigForm,
    user: SysUserDetails = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    return Result(data=await ConfigService(db).create(form))


@router.put("/{config_id}", summary="更新配置", dependencies=[Depends(require_perm("sys:config:update"))])
@operation_log(module=LogModuleEnum.CONFIG, action_type=ActionTypeEnum.UPDATE, title="修改配置")
async def update_config(
    request: Request,
    config_id: int,
    form: ConfigForm,
    user: SysUserDetails = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return Result(data=await ConfigService(db).update(config_id, form))


@router.delete("/{ids}", summary="删除配置", dependencies=[Depends(require_perm("sys:config:delete"))])
@operation_log(module=LogModuleEnum.CONFIG, action_type=ActionTypeEnum.DELETE, title="删除配置")
async def delete_configs(
    request: Request,
    ids: str,
    user: SysUserDetails = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return Result(data=await ConfigService(db).delete(ids))
