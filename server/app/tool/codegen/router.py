"""代码生成路由。"""

import io
import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.database import get_db
from app.dependencies import get_current_user, require_perm
from app.pagination import PageResult
from app.response import Result
from app.tool.codegen.schemas import GenConfigForm, PreviewQuery, TableQuery
from app.tool.codegen.service import CodegenService

router = APIRouter(prefix="/api/v1/codegen", tags=["代码生成"], dependencies=[Depends(get_current_user)])

_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9_.-]+")


def _zip_filename(table_name: str) -> str:
    """下载文件名只保留 ASCII 安全字符，避免响应头注入与乱码。"""
    safe = _SAFE_FILENAME.sub("_", table_name).strip("_")
    return f"{safe or 'codegen'}_codegen.zip"


@router.get(
    "/table",
    summary="获取数据表分页列表",
    dependencies=[Depends(require_perm("sys:codegen:list"))],
)
async def get_table_page(
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keywords: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    data = await CodegenService(db).get_table_page(TableQuery(pageNum=pageNum, pageSize=pageSize, keywords=keywords))
    return Result(
        data=PageResult(
            records=data["list"],
            total=data["total"],
            pageNum=pageNum,
            pageSize=pageSize,
        )
    )


@router.get(
    "/{table_name}/config",
    summary="获取代码生成配置",
    dependencies=[Depends(require_perm("sys:codegen:list"))],
)
async def get_gen_config(table_name: str, db: AsyncSession = Depends(get_db)):
    return Result(data=(await CodegenService(db).get_gen_config(table_name)).model_dump(by_alias=True))


@router.post(
    "/{table_name}/config", summary="保存代码生成配置", dependencies=[Depends(require_perm("sys:codegen:update"))]
)
async def save_gen_config(table_name: str, form: GenConfigForm, db: AsyncSession = Depends(get_db)):
    await CodegenService(db).save_gen_config(table_name, form)
    return Result(data=None)


@router.delete(
    "/{table_name}/config", summary="删除代码生成配置", dependencies=[Depends(require_perm("sys:codegen:update"))]
)
async def delete_gen_config(table_name: str, db: AsyncSession = Depends(get_db)):
    await CodegenService(db).delete_gen_config(table_name)
    return Result(data=None)


@router.get(
    "/{table_name}/preview",
    summary="获取预览生成代码",
    dependencies=[Depends(require_perm("sys:codegen:list"))],
)
async def preview_code(
    table_name: str,
    params: PreviewQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    data = await CodegenService(db).preview_code(table_name, params.page_type, params.frontend_type)
    return Result(data=[d.model_dump(by_alias=True) for d in data])


@router.get(
    "/{table_name}/download",
    summary="下载代码",
    dependencies=[Depends(require_perm("sys:codegen:list"))],
)
async def download_code(
    table_name: str,
    params: PreviewQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    zip_bytes = await CodegenService(db).download_code(table_name, params.page_type, params.frontend_type)
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{_zip_filename(table_name)}"'},
    )
