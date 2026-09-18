"""操作日志管理。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select, cast, String, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field, field_serializer
import re

from app.serializers import BigId

from datetime import date, datetime, time, timedelta

from app.database import get_db
from app.pagination import PageResult
from app.dependencies import get_current_user, require_perm
from app.auth.schemas import SysUserDetails
from app.constants import ROOT_ROLE_CODE
from app.system.log.operation_log import operation_log
from app.system.log.constants import ActionTypeEnum, LogModuleEnum
from app.response import Result
from app.system.log.models import SysLog

router = APIRouter(prefix="/api/v1/logs", tags=["日志管理"])


async def require_log_admin(user: SysUserDetails = Depends(get_current_user)) -> SysUserDetails:
    if not (user.isRoot or user.roles.intersection({ROOT_ROLE_CODE, "ROOT", "ADMIN"})):
        raise HTTPException(status_code=403, detail="仅管理员可以清理历史日志")
    return user


def history_cutoff(before_date: date) -> datetime:
    if before_date > date.today():
        raise HTTPException(status_code=422, detail="截止日期不能晚于今天")
    return datetime.combine(before_date, time.min)


class LogQuery(BaseModel):
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    module: int | None = None
    actionType: int | None = None
    keywords: str | None = None
    status: int | None = None
    createTime: list[date] | None = Field(default=None, min_length=2, max_length=2)


class LogVO(BaseModel):
    id: BigId | None = None
    module: int | None = None
    actionType: int | None = None
    title: str | None = None
    content: str | None = None
    requestMethod: str | None = None
    requestUri: str | None = None
    ip: str | None = None
    province: str | None = None
    city: str | None = None
    device: str | None = None
    os: str | None = None
    browser: str | None = None
    status: int | None = None
    errorMsg: str | None = None
    executionTime: int | None = None
    operatorId: BigId | None = None
    operatorName: str | None = None
    createTime: datetime | None = None
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=lambda name: AliasChoices(name, re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower())
        ),
    )

    @field_serializer("createTime")
    def serialize_create_time(self, value: datetime | None) -> str | None:
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


class VisitTrendVO(BaseModel):
    dates: list[str]
    pvList: list[int]
    uvList: list[int]


class VisitOverviewVO(BaseModel):
    todayUvCount: int = 0
    totalUvCount: int = 0
    uvGrowthRate: float = 0.0
    todayPvCount: int = 0
    totalPvCount: int = 0
    pvGrowthRate: float = 0.0


class LogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_history(self, before_date: date) -> int:
        return (await self.db.execute(
            select(func.count()).select_from(SysLog).where(SysLog.create_time < history_cutoff(before_date))
        )).scalar() or 0

    async def clear_history(self, before_date: date) -> int:
        result = await self.db.execute(delete(SysLog).where(SysLog.create_time < history_cutoff(before_date)))
        return result.rowcount

    async def get_page(self, query: LogQuery) -> PageResult:
        conditions = []
        if query.module is not None:
            conditions.append(SysLog.module == query.module)
        if query.actionType is not None:
            conditions.append(SysLog.action_type == query.actionType)
        if query.status is not None:
            conditions.append(SysLog.status == query.status)
        if query.keywords:
            kw = f"%{query.keywords}%"
            conditions.append(
                SysLog.title.ilike(kw)
                | SysLog.operator_name.ilike(kw)
                | cast(SysLog.ip, String).ilike(kw)
            )
        if query.createTime:
            start_date, end_date = query.createTime
            if start_date > end_date:
                raise HTTPException(status_code=422, detail="开始日期不能晚于结束日期")
            conditions.extend([
                SysLog.create_time >= datetime.combine(start_date, time.min),
                SysLog.create_time < datetime.combine(end_date + timedelta(days=1), time.min),
            ])

        stmt = select(SysLog)
        if conditions:
            stmt = stmt.where(*conditions)
        base = stmt
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
        offset = (query.pageNum - 1) * query.pageSize
        rows = await self.db.execute(
            stmt.order_by(SysLog.create_time.desc()).offset(offset).limit(query.pageSize)
        )
        vo_list = [LogVO.model_validate(r, from_attributes=True) for r in rows.scalars().all()]
        return PageResult(records=vo_list, total=total, pageNum=query.pageNum, pageSize=query.pageSize)

    async def get_visit_trend(self, start_date: date, end_date: date) -> VisitTrendVO:
        s = start_date
        e = end_date
        if s > e:
            raise HTTPException(status_code=422, detail="开始日期不能晚于结束日期")
        dates = []
        cur = s
        while cur <= e:
            dates.append(cur.isoformat())
            cur += timedelta(days=1)

        start_dt = datetime.combine(s, time.min)
        end_dt = datetime.combine(e + timedelta(days=1), time.min)

        # PV counts per date
        pv_rows = await self.db.execute(
            select(func.date(SysLog.create_time), func.count())
            .where(SysLog.create_time >= start_dt, SysLog.create_time < end_dt)
            .group_by(func.date(SysLog.create_time))
        )
        pv_map = {str(d): c for d, c in pv_rows}

        # UV counts per date (distinct ip)
        ip_rows = await self.db.execute(
            select(func.date(SysLog.create_time), func.count(func.distinct(SysLog.ip)))
            .where(SysLog.create_time >= start_dt, SysLog.create_time < end_dt)
            .group_by(func.date(SysLog.create_time))
        )
        uv_map = {str(d): c for d, c in ip_rows}

        return VisitTrendVO(
            dates=dates,
            pvList=[pv_map.get(d, 0) for d in dates],
            uvList=[uv_map.get(d, 0) for d in dates],
        )

    async def get_visit_overview(self) -> VisitOverviewVO:
        today = date.today()
        yesterday = today - timedelta(days=1)

        # today UV
        r = await self.db.execute(
            select(func.count(func.distinct(SysLog.ip)))
            .where(func.date(SysLog.create_time) == today)
        )
        today_uv = r.scalar() or 0

        # yesterday UV
        r = await self.db.execute(
            select(func.count(func.distinct(SysLog.ip)))
            .where(func.date(SysLog.create_time) == yesterday)
        )
        yest_uv = r.scalar() or 0

        # total UV
        r = await self.db.execute(select(func.count(func.distinct(SysLog.ip))))
        total_uv = r.scalar() or 0

        # today PV
        r = await self.db.execute(
            select(func.count()).where(func.date(SysLog.create_time) == today)
        )
        today_pv = r.scalar() or 0

        # yesterday PV
        r = await self.db.execute(
            select(func.count()).where(func.date(SysLog.create_time) == yesterday)
        )
        yest_pv = r.scalar() or 0

        # total PV
        r = await self.db.execute(select(func.count()).select_from(SysLog))
        total_pv = r.scalar() or 0

        uv_rate = round((today_uv - yest_uv) / yest_uv * 100, 2) if yest_uv else 0.0
        pv_rate = round((today_pv - yest_pv) / yest_pv * 100, 2) if yest_pv else 0.0

        return VisitOverviewVO(
            todayUvCount=today_uv,
            totalUvCount=total_uv,
            uvGrowthRate=uv_rate,
            todayPvCount=today_pv,
            totalPvCount=total_pv,
            pvGrowthRate=pv_rate,
        )


@router.get("", summary="日志分页", dependencies=[Depends(require_perm("sys:log:list"))])
async def get_logs(
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    module: int | None = None,
    actionType: int | None = None,
    status: int | None = None,
    keywords: str | None = None,
    createTime: list[date] | None = Query(default=None, min_length=2, max_length=2),
    db: AsyncSession = Depends(get_db),
):
    q = LogQuery(
        pageNum=pageNum, pageSize=pageSize, module=module, actionType=actionType,
        status=status, keywords=keywords, createTime=createTime,
    )
    return Result(data=await LogService(db).get_page(q))


@router.get("/analytics/trend", summary="访问趋势统计")
async def get_visit_trend(
    startDate: date = Query(..., description="开始时间 yyyy-MM-dd"),
    endDate: date = Query(..., description="结束时间 yyyy-MM-dd"),
    db: AsyncSession = Depends(get_db),
):
    return Result(data=await LogService(db).get_visit_trend(startDate, endDate))


@router.get("/analytics/overview", summary="访问统计概览")
async def get_visit_overview(db: AsyncSession = Depends(get_db)):
    return Result(data=await LogService(db).get_visit_overview())


@router.get("/history/count", summary="预览历史日志清理数量")
async def count_log_history(
    beforeDate: date = Query(...),
    user: SysUserDetails = Depends(require_log_admin),
    db: AsyncSession = Depends(get_db),
):
    return Result(data={"count": await LogService(db).count_history(beforeDate)})


@router.delete("/history", summary="管理员清理历史日志")
@operation_log(module=LogModuleEnum.LOG, action_type=ActionTypeEnum.DELETE, title="清理历史日志")
async def clear_log_history(
    request: Request,
    beforeDate: date = Query(...),
    user: SysUserDetails = Depends(require_log_admin),
    db: AsyncSession = Depends(get_db),
):
    count = await LogService(db).clear_history(beforeDate)
    await db.commit()
    request.state.operation_log_content = f"清理 {beforeDate.isoformat()} 之前的历史日志，共 {count} 条（不含当天）"
    return Result(data={"deletedCount": count})
