"""代码生成功能回归测试。

覆盖评审中确认的缺陷：生成模型重复声明基础 Mixin 列、系统列被当作表单字段、
目录命名不符合项目约定、查询控件缺失、逻辑删除未过滤、CURD 页面类型无效等。
"""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.exceptions import BusinessException
from app.tool.codegen.service import (
    CodegenService,
    build_import_lines,
    default_field_options,
    infer_form_type,
    infer_query_type,
    normalize_form_width,
    sa_column_spec,
    sanitize_text,
    to_snake,
)

SERVER_ROOT = Path(__file__).resolve().parents[1]

# (列名, udt, data_type, 可空, 注释, 是否主键, 长度, 精度, 小数位)
SAMPLE_COLUMNS = [
    ("id", "int8", "bigint", False, "主键ID", True, None, 64, 0),
    ("name", "varchar", "character varying", False, "名称", False, 50, None, None),
    ("status", "int2", "smallint", False, "状态", False, None, 16, 0),
    ("remark", "text", "text", True, "备注", False, None, None, None),
    ("price", "numeric", "numeric", True, "价格", False, None, 10, 2),
    ("publish_date", "date", "date", True, "发布日期", False, None, None, None),
    ("create_time", "timestamp", "timestamp without time zone", True, "创建时间", False, None, None, None),
    ("update_time", "timestamp", "timestamp without time zone", True, "更新时间", False, None, None, None),
    ("is_deleted", "int2", "smallint", False, "逻辑删除", False, None, 16, 0),
]

TABLE = "demo_order_info"


def make_columns(rows: list[tuple]) -> list[dict]:
    """把便捷元组转换为 _get_columns 的返回结构。"""
    return [
        {
            "name": name,
            "udt": udt,
            "data_type": data_type,
            "is_nullable": nullable,
            "comment": comment,
            "is_pk": is_pk,
            "max_length": max_length,
            "precision": precision,
            "scale": scale,
        }
        for (name, udt, data_type, nullable, comment, is_pk, max_length, precision, scale) in rows
    ]


def saved_column(**overrides) -> SimpleNamespace:
    """构造一条已保存的字段配置。"""
    values = {
        "column_name": None,
        "field_name": "",
        "field_type": None,
        "frontend_type": None,
        "field_comment": None,
        "query_name": None,
        "list_name": None,
        "list_width": None,
        "list_ellipsis": 1,
        "is_show_in_list": None,
        "is_show_in_create": None,
        "is_show_in_update": None,
        "is_show_in_query": None,
        "is_required": None,
        "max_length": None,
        "form_type": None,
        "query_type": None,
        "dict_type": None,
        "field_sort": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def saved_table(**overrides) -> SimpleNamespace:
    """构造一条已保存的表配置。"""
    values = {
        "id": 1,
        "table_name": TABLE,
        "module_name": "demo",
        "package_name": "com.youlai.fastapi",
        "business_name": "订单信息",
        "entity_name": "DemoOrderInfo",
        "author": "youlai",
        "parent_menu_id": None,
        "remove_table_prefix": "demo_",
        "page_type": "classic",
        "form_enabled": 1,
        "form_layout": "dialog",
        "form_width": "600px",
        "form_columns": 2,
        "delete_enabled": 1,
        "delete_mode": "logical",
        "delete_type": "single_batch",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class StubService(CodegenService):
    """绕过数据库，直接对固定列元数据与配置渲染模板。"""

    def __init__(self, columns: list[dict], table=None, saved: dict | None = None):
        self.db = None
        self._columns = columns
        self._table = table
        self._saved = saved or {}

    async def _get_columns(self, table_name: str) -> list[dict]:
        return self._columns

    async def _load_saved_config(self, table_name: str):
        return self._table, self._saved


@pytest.fixture
def clean_metadata():
    """回收测试期间注册到 Base.metadata 的表，避免影响其它测试。"""
    from app.database import Base

    before = set(Base.metadata.tables)
    yield
    for name in list(Base.metadata.tables):
        if name not in before:
            Base.metadata.remove(Base.metadata.tables[name])


async def render(
    columns: list[dict] | None = None,
    *,
    table=None,
    saved: dict | None = None,
    page_type: str = "classic",
    frontend_type: str = "ts",
) -> dict[str, str]:
    """渲染全部生成产物，键为 "<path>/<file_name>"。"""
    service = StubService(columns or make_columns(SAMPLE_COLUMNS), table, saved)
    files = await service._collect_files(TABLE, page_type, frontend_type)
    return {f"{f['path']}/{f['file_name']}": f["content"] for f in files}


# ── 生成的 ORM 模型 ──


@pytest.mark.anyio
async def test_generated_model_reuses_base_mixins(clean_metadata):
    """回归：重复声明 create_time/update_time/is_deleted 会触发 DuplicateColumnError。"""
    files = await render(make_columns(SAMPLE_COLUMNS))
    source = files["server/app/demo/demo_order_info/models.py"]

    namespace: dict = {}
    exec(compile(source, "models.py", "exec"), namespace)  # noqa: S102 - 校验生成代码可导入
    model = namespace["DemoOrderInfo"]

    assert {"create_time", "update_time", "is_deleted"} <= set(model.__table__.columns.keys())
    # 模型属性与数据库列同名（项目 ORM 约定）
    assert "publish_date" in model.__table__.columns
    assert model.__table__.c.name.type.length == 50
    assert str(model.__table__.c.price.type) == "NUMERIC(10, 2)"


@pytest.mark.anyio
async def test_generated_model_skips_mixins_for_plain_table(clean_metadata):
    """表里没有审计列时不应继承 TimestampMixin / SoftDeleteMixin。"""
    columns = make_columns(
        [
            ("id", "int8", "bigint", False, "主键ID", True, None, 64, 0),
            ("title", "varchar", "character varying", False, "标题", False, 100, None, None),
        ]
    )
    service = StubService(columns, saved_table(table_name="codegen_probe_plain", entity_name="ProbePlain"))
    context = await service._build_template_context("codegen_probe_plain")
    source = next(
        f["content"] for f in service._render_files(context, "classic", "ts") if f["file_name"] == "models.py"
    )

    namespace: dict = {}
    exec(compile(source, "models.py", "exec"), namespace)  # noqa: S102 - 校验生成代码可导入
    model = namespace["ProbePlain"]

    assert set(model.__table__.columns.keys()) == {"id", "title"}
    assert not hasattr(model, "is_deleted")


# ── 命名与路径 ──


@pytest.mark.anyio
async def test_generated_paths_follow_project_conventions():
    files = await render()
    assert "server/app/demo/demo_order_info/models.py" in files
    assert "web/src/api/demo/demo-order-info/index.ts" in files
    assert "web/src/views/demo/demo-order-info/index.vue" in files
    assert "app/src/api/demo-order-info.ts" in files
    assert "app/src/subPages/work/demo-order-info/index.vue" in files


@pytest.mark.anyio
async def test_generated_imports_use_absolute_module_path():
    files = await render()
    service = files["server/app/demo/demo_order_info/service.py"]
    assert "from app.demo.demo_order_info.models import DemoOrderInfo" in service


# ── 表单 / 查询字段 ──


@pytest.mark.anyio
async def test_audit_columns_are_not_form_fields():
    files = await render()
    schemas = files["server/app/demo/demo_order_info/schemas.py"]
    create_body = schemas.split("class DemoOrderInfoCreate")[1].split("class DemoOrderInfoUpdate")[0]
    assert "createTime" not in create_body
    assert "updateTime" not in create_body
    assert "isDeleted" not in create_body
    # 审计时间仍需出现在 VO 中，便于列表按需展示
    assert "createTime" in schemas.split("class DemoOrderInfoVO")[1]


@pytest.mark.anyio
async def test_classic_page_renders_control_for_every_query_type():
    """回归：布尔/字典类查询条件曾经渲染成空的 el-form-item。"""
    files = await render()
    vue = files["web/src/views/demo/demo-order-info/index.vue"]
    search_form = vue.split("</el-card>")[0]

    assert 'label="状态"' in search_form
    status_block = search_form.split('label="状态"')[1].split("</el-form-item>")[0]
    assert "el-select" in status_block
    # 日期范围查询使用 daterange + BETWEEN
    assert 'type="daterange"' in search_form
    # 不存在空白的查询项
    assert "<el-form-item label=\"备注\" prop=\"remark\">\n        </el-form-item>" not in search_form


@pytest.mark.anyio
async def test_query_params_accept_range_values():
    files = await render()
    schemas = files["server/app/demo/demo_order_info/schemas.py"]
    assert "publishDate: list[date] | date | None" in schemas
    router = files["server/app/demo/demo_order_info/router.py"]
    assert "publishDate: list[str] | str | None = Query(default=None)" in router


# ── 删除策略 ──


@pytest.mark.anyio
async def test_logical_delete_filters_soft_deleted_rows():
    files = await render(table=saved_table(delete_mode="logical"))
    service = files["server/app/demo/demo_order_info/service.py"]
    assert "conditions = [DemoOrderInfo.is_deleted == 0]" in service
    assert "values(is_deleted=1)" in service
    assert "delete(DemoOrderInfo)" not in service


@pytest.mark.anyio
async def test_physical_delete_uses_delete_statement():
    files = await render(table=saved_table(delete_mode="physical"))
    service = files["server/app/demo/demo_order_info/service.py"]
    assert "delete(DemoOrderInfo).where(DemoOrderInfo.id.in_(id_list))" in service
    assert "values(is_deleted=1)" not in service


@pytest.mark.anyio
async def test_logical_delete_falls_back_when_column_missing():
    """表里没有 is_deleted 时不能生成假删 SQL。"""
    columns = make_columns(
        [
            ("id", "int8", "bigint", False, "主键ID", True, None, 64, 0),
            ("title", "varchar", "character varying", False, "标题", False, 100, None, None),
        ]
    )
    files = await render(columns, table=saved_table(delete_mode="logical"))
    service = files["server/app/demo/demo_order_info/service.py"]
    assert "is_deleted=1" not in service
    init = files["server/app/demo/demo_order_info/__init__.py"]
    assert "物理删除" in init


# ── 字段类型与配置覆盖 ──


@pytest.mark.anyio
async def test_field_type_and_name_overrides_are_applied():
    saved = {
        "publish_date": saved_column(
            column_name="publish_date",
            field_name="publishDay",
            field_type="str",
            frontend_type="string",
            field_comment="发布日",
        )
    }
    files = await render(saved=saved)
    schemas = files["server/app/demo/demo_order_info/schemas.py"]
    models = files["server/app/demo/demo_order_info/models.py"]
    service = files["server/app/demo/demo_order_info/service.py"]

    # 模型属性保持列名，Schema 通过 validation_alias 取值
    assert "publish_date: Mapped[" in models
    assert 'publishDay: str | None = Field(default=None, validation_alias="publish_date"' in schemas
    assert "publish_date=form.publishDay" in service


@pytest.mark.anyio
async def test_unknown_column_type_is_rejected():
    saved = {"name": saved_column(column_name="name", field_name="name", field_type="bytes")}
    with pytest.raises(BusinessException):
        await render(saved=saved)


# ── 页面类型 ──


@pytest.mark.anyio
async def test_curd_page_generates_framework_files():
    files = await render(table=saved_table(page_type="curd"), page_type="curd")
    assert "web/src/views/demo/demo-order-info/config/search.ts" in files
    assert "web/src/views/demo/demo-order-info/config/content.ts" in files
    assert "web/src/views/demo/demo-order-info/config/add.ts" in files
    assert "web/src/views/demo/demo-order-info/config/edit.ts" in files

    vue = files["web/src/views/demo/demo-order-info/index.vue"]
    assert "<page-search" in vue
    assert "<page-content" in vue
    assert "<page-modal" in vue
    content = files["web/src/views/demo/demo-order-info/config/content.ts"]
    assert 'indexAction(params)' in content
    assert "deleteAction: DemoOrderInfoAPI.deleteByIds" in content


@pytest.mark.anyio
async def test_classic_page_does_not_generate_curd_configs():
    files = await render(page_type="classic")
    assert not any(path.endswith("config/search.ts") for path in files)


@pytest.mark.anyio
async def test_javascript_frontend_type_is_rejected():
    with pytest.raises(BusinessException):
        await render(frontend_type="js")


@pytest.mark.anyio
async def test_unknown_page_type_is_rejected():
    with pytest.raises(BusinessException):
        await render(page_type="legacy")


# ── 菜单 SQL ──


@pytest.mark.anyio
async def test_menu_sql_generated_only_with_parent_menu():
    assert not any(path.endswith("_menu.sql") for path in await render())

    files = await render(table=saved_table(parent_menu_id=201), page_type="curd")
    sql = files["server/sql/demo_order_info_menu.sql"]
    assert "DO $$" in sql
    assert "v_parent_id bigint := 201" in sql
    assert "'demo:demo-order-info'" in sql
    assert "'demo/demo-order-info/index'" in sql
    assert "v_perm_prefix || ':list'" in sql
    assert "v_perm_prefix || ':create'" in sql
    assert "v_perm_prefix || ':update'" in sql
    assert "v_perm_prefix || ':delete'" in sql


@pytest.mark.anyio
async def test_menu_sql_escapes_single_quotes():
    files = await render(table=saved_table(parent_menu_id=1, business_name="订单'信息"), page_type="curd")
    sql = files["server/sql/demo_order_info_menu.sql"]
    assert "'订单''信息'" in sql


# ── 纯函数 ──


def test_to_snake_handles_pascal_and_kebab():
    assert to_snake("DemoOrderInfo") == "demo_order_info"
    assert to_snake("demo-order-info") == "demo_order_info"
    assert to_snake("OrderInfo") == "order_info"
    assert to_snake("APIKey") == "api_key"
    assert to_snake("") == ""


def test_sa_column_spec_keeps_length_and_precision():
    assert sa_column_spec("varchar", max_length=50) == "String(50)"
    assert sa_column_spec("numeric", precision=10, scale=2) == "Numeric(10, 2)"
    assert sa_column_spec("int8") == "BigInteger"
    assert sa_column_spec("unknown_type") == "String(255)"


def test_default_field_options_skips_system_columns():
    for column in ("id", "create_time", "update_time", "is_deleted", "create_by", "update_by"):
        options = default_field_options(column, column, "str", False, True)
        assert options["is_show_in_list"] == 0
        assert options["is_show_in_create"] == 0
        assert options["is_show_in_query"] == 0

    options = default_field_options("name", "name", "str", False, False)
    assert options == {
        "form_type_name": "INPUT",
        "query_type_name": "LIKE",
        "is_show_in_list": 1,
        "is_show_in_create": 1,
        "is_show_in_update": 1,
        "is_show_in_query": 1,
        "is_required": 1,
    }


def test_infer_form_and_query_type():
    assert infer_form_type("status", "int") == "BOOLEAN_SELECT"
    assert infer_form_type("publish_date", "date") == "DATE"
    assert infer_form_type("remark", "str") == "TEXT_AREA"
    assert infer_form_type("price", "Decimal") == "INPUT_NUMBER"
    assert infer_query_type("DATE", "date") == "BETWEEN"
    assert infer_query_type("DATE_TIME", "datetime") == "BETWEEN"
    assert infer_query_type("INPUT", "str") == "LIKE"
    assert infer_query_type("INPUT_NUMBER", "int") == "EQ"


def test_sanitize_text_blocks_literal_breakout():
    assert sanitize_text('bad"name') == "bad name"
    assert sanitize_text("line1\nline2") == "line1 line2"
    assert sanitize_text("close */ comment") == "close * / comment"
    assert sanitize_text("${jndi}") == "$ {jndi}"
    assert sanitize_text("", "兜底") == "兜底"


def test_normalize_form_width_rejects_injection():
    assert normalize_form_width("600") == "600px"
    assert normalize_form_width("80%") == "80%"
    with pytest.raises(BusinessException):
        normalize_form_width('600px" onmouseover="alert(1)')


def test_build_import_lines_inserts_group_blank_line():
    lines = build_import_lines([["from a import b"], [], ["from c import d"]])
    assert lines == ["from a import b", "", "from c import d"]


@pytest.mark.anyio
async def test_generated_python_is_syntactically_valid():
    """所有生成的后端文件都必须能通过 AST 解析。"""
    files = await render(table=saved_table(parent_menu_id=201), page_type="curd")
    assert any(path.endswith(".py") for path in files)
    for path, content in files.items():
        if path.endswith(".py"):
            ast.parse(content, filename=path)


@pytest.mark.anyio
async def test_generated_content_uses_lf_line_endings():
    """生成内容统一 LF：写盘/打包不应引入平台相关的 CRLF。"""
    files = await render(table=saved_table(parent_menu_id=201), page_type="curd")
    for path, content in files.items():
        assert "\r" not in content, path
        assert content.endswith("\n"), path
        assert "[[" not in content and "]]" not in content, path


def test_codegen_permissions_exist_in_seed_sql():
    """路由用到的权限标识必须能在初始化脚本里找到，否则非超管无法操作。"""
    seed = (SERVER_ROOT / "sql" / "postgresql" / "youlai-admin.sql").read_text(encoding="utf-8")
    assert "'sys:codegen:list'" in seed
    assert "'sys:codegen:update'" in seed
