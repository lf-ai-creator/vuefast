"""代码生成服务 — 元数据查询 + Jinja2 渲染 + 配置持久化 + zip 打包。

设计要点（与项目技术栈保持一致）：

1. 生成的 ORM 模型使用与数据库列同名的小写下划线属性，并由 ``app.database``
   的 ``BaseIdMixin`` / ``TimestampMixin`` / ``SoftDeleteMixin`` 提供主键和时间戳，
   不再重复声明这些列（重复声明会触发 SQLAlchemy ``DuplicateColumnError``）。
2. Schemas 使用小驼峰字段名（对外 JSON 契约），当字段名与列名不一致时通过
   ``validation_alias`` 从 ORM 对象取值，避免手工拼装 VO。
3. 目录与文件命名遵循项目约定：后端包为下划线目录，Web 为短横线目录。
"""

import io
import keyword
import re
import zipfile
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import delete as sa_delete
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BusinessException
from app.response import ResultCode
from app.tool.codegen.models import GenTable, GenTableColumn
from app.tool.codegen.schemas import (
    FieldConfigVO,
    GenConfigForm,
    GenConfigVO,
    PreviewVO,
    TableQuery,
    TableVO,
)

_TEMPLATE_DIR = Path(__file__).parent / "templates"

# ═══════════════════════════════════════════════════════════
# PostgreSQL → Python 类型 / SQLAlchemy 类型 / TypeScript 类型
# ═══════════════════════════════════════════════════════════

_PY_TYPE: dict[str, str] = {
    "int2": "int",
    "smallint": "int",
    "int4": "int",
    "integer": "int",
    "int8": "int",
    "bigint": "int",
    "float4": "float",
    "real": "float",
    "float8": "float",
    "double precision": "float",
    "numeric": "Decimal",
    "decimal": "Decimal",
    "bool": "bool",
    "boolean": "bool",
    "varchar": "str",
    "char": "str",
    "bpchar": "str",
    "text": "str",
    "name": "str",
    "citext": "str",
    "uuid": "str",
    "json": "dict",
    "jsonb": "dict",
    "timestamp": "datetime",
    "timestamptz": "datetime",
    "date": "date",
    "time": "time",
}

# SQLAlchemy 列类型名（长度/精度由 information_schema 提供，拼装见 _sa_column_spec）
_SA_TYPE: dict[str, str] = {
    "int2": "SmallInteger",
    "smallint": "SmallInteger",
    "int4": "Integer",
    "integer": "Integer",
    "int8": "BigInteger",
    "bigint": "BigInteger",
    "float4": "Float",
    "real": "Float",
    "float8": "Float",
    "double precision": "Float",
    "numeric": "Numeric",
    "decimal": "Numeric",
    "bool": "Boolean",
    "boolean": "Boolean",
    "varchar": "String",
    "char": "String",
    "bpchar": "String",
    "text": "Text",
    "name": "String",
    "citext": "String",
    "uuid": "Uuid",
    "json": "JSON",
    "jsonb": "JSON",
    "timestamp": "DateTime",
    "timestamptz": "DateTime",
    "date": "Date",
    "time": "Time",
}

_TS_TYPE: dict[str, str] = {
    "int": "number",
    "float": "number",
    "Decimal": "number",
    "bool": "boolean",
    "str": "string",
    "dict": "Record<string, any>",
    "datetime": "string",
    "date": "string",
    "time": "string",
}

# 前端类型下拉可选值（web/src/views/codegen/components/FieldDefinitionStep.vue）
_FRONTEND_TYPES = frozenset(
    {"string", "number", "boolean", "Date", "string[]", "number[]", "Record<string, any>", "any"}
)

_FORM_TYPE = {
    "INPUT": 1,
    "SELECT": 2,
    "RADIO": 3,
    "CHECK_BOX": 4,
    "INPUT_NUMBER": 5,
    "SWITCH": 6,
    "TEXT_AREA": 7,
    "DATE": 8,
    "DATE_TIME": 9,
    "HIDDEN": 10,
    "BOOLEAN_SELECT": 11,
    "ENUM_SELECT": 12,
    "DICT_SELECT": 13,
    "FILE_UPLOAD": 14,
}
_FORM_TYPE_REV = {v: k for k, v in _FORM_TYPE.items()}

_QUERY_TYPE = {
    "EQ": 1,
    "LIKE": 2,
    "IN": 3,
    "BETWEEN": 4,
    "GT": 5,
    "GE": 6,
    "LT": 7,
    "LE": 8,
    "NE": 9,
    "LIKE_LEFT": 10,
    "LIKE_RIGHT": 11,
}
_QUERY_TYPE_REV = {v: k for k, v in _QUERY_TYPE.items()}

# ── 基础模型列 / 非业务列 ──

_ID_COLUMN = "id"
_TIMESTAMP_COLUMNS = ("create_time", "update_time")
_SOFT_DELETE_COLUMN = "is_deleted"

# 不参与列表/查询/表单默认勾选的审计列（create_by/update_by 仍需映射为模型字段）
_NON_BUSINESS_COLUMNS = frozenset({"id", "create_time", "update_time", "is_deleted", "create_by", "update_by"})

# 表单类型 → 生成控件（Web 普通页面弹窗表单）
_FORM_CONTROL = {
    "INPUT": "input",
    "TEXT_AREA": "textarea",
    "INPUT_NUMBER": "number",
    "SELECT": "select",
    "ENUM_SELECT": "select",
    "DICT_SELECT": "dict-select",
    "BOOLEAN_SELECT": "boolean-select",
    "SWITCH": "switch",
    "RADIO": "radio",
    "CHECK_BOX": "checkbox",
    "FILE_UPLOAD": "file",
    "DATE": "date",
    "DATE_TIME": "datetime",
    "HIDDEN": "hidden",
}

# 表单控件 → 查询控件（Web 普通页面搜索表单）
_QUERY_CONTROL = {
    "input": "input",
    "textarea": "input",
    "number": "number",
    "select": "select",
    "dict-select": "dict-select",
    "boolean-select": "boolean-select",
    "switch": "boolean-select",
    "radio": "radio",
    "checkbox": "checkbox",
    "date": "date",
    "datetime": "datetime",
    "file": "none",
    "hidden": "none",
}

# 查询控件 → CURD PageSearch 组件类型（仅支持 input/select/input-number/date-picker 等）
_CURD_SEARCH_TYPE = {
    "input": "input",
    "number": "input-number",
    "select": "select",
    "dict-select": "select",
    "boolean-select": "select",
    "radio": "select",
    "checkbox": "select",
    "date": "date-picker",
    "datetime": "date-picker",
}

# 表单控件 → CURD PageModal 组件类型；字典与文件上传走 custom 插槽
_CURD_MODAL_TYPE = {
    "input": "input",
    "textarea": "input",
    "number": "input-number",
    "select": "select",
    "dict-select": "custom",
    "boolean-select": "radio",
    "switch": "switch",
    "radio": "radio",
    "checkbox": "checkbox",
    "file": "custom",
    "date": "date-picker",
    "datetime": "date-picker",
    "hidden": "input",
}

# 需要以「选择」方式交互的控件，校验提示与触发方式不同于文本输入
_SELECT_LIKE_CONTROLS = frozenset(
    {"select", "dict-select", "boolean-select", "switch", "radio", "checkbox", "file", "date", "datetime"}
)


def pg_to_python(udt: str) -> str:
    """PostgreSQL udt 名称 → Python 类型名。"""
    return _PY_TYPE.get(udt, "str")


def sa_type_name(udt: str) -> str:
    """PostgreSQL udt 名称 → SQLAlchemy 类型名（不含长度/精度）。"""
    return _SA_TYPE.get(udt, "String")


def sa_column_spec(
    udt: str,
    max_length: int | None = None,
    precision: int | None = None,
    scale: int | None = None,
) -> str:
    """拼装 SQLAlchemy 列类型表达式，保留数据库中的长度与精度。"""
    type_name = sa_type_name(udt)
    if type_name == "String":
        return f"String({max_length})" if max_length else "String(255)"
    if type_name == "Numeric":
        if precision:
            return f"Numeric({precision}, {scale or 0})"
        return "Numeric(18, 2)"
    return type_name


def py_to_ts(py_type: str) -> str:
    """Python 类型名 → TypeScript 类型。"""
    return _TS_TYPE.get(py_type, "any")


def form_type_name(i: int | None) -> str:
    return _FORM_TYPE_REV.get(i or 0, "INPUT")


def query_type_name(i: int | None) -> str:
    return _QUERY_TYPE_REV.get(i or 0, "EQ")


def pascal_case(s: str) -> str:
    return "".join(w[:1].upper() + w[1:] for w in s.split("_") if w)


def lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else ""


def snake_to_camel(s: str) -> str:
    """将数据库下划线列名转换为前端与 Python 均可使用的小驼峰命名。"""
    parts = [part for part in s.split("_") if part]
    if not parts:
        return s
    return parts[0].lower() + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def to_snake(value: str) -> str:
    """PascalCase / camelCase / kebab-case → snake_case，用于生成目录与模块名。"""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value or "")
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


def is_valid_identifier(value: str) -> bool:
    """判断生成代码中会作为 Python 标识符使用的名称（排除 Python 关键字）。"""
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value or "")) and not keyword.iskeyword(value)


_UNSAFE_TEXT = re.compile(r"""[\r\n\t\\`"]+""")


def sanitize_text(value: str | None, fallback: str = "") -> str:
    """清理会破坏生成代码字符串字面量或注释的用户可控文本。

    字段描述、业务名、作者都来自配置与数据库注释，未清理时可以提前闭合
    三引号/双引号/块注释，造成生成代码语法错误甚至代码注入。
    """
    text = _UNSAFE_TEXT.sub(" ", value or "").replace("*/", "* /").replace("${", "$ {")
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text or fallback


def normalize_form_width(value: str | None) -> str:
    """规范表单容器宽度，避免配置被直接注入到生成的 Vue 属性中。"""
    width = (value or "600px").strip()
    if re.fullmatch(r"\d+", width):
        return f"{width}px"
    if re.fullmatch(r"\d+(?:px|%)", width):
        return width
    raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="表单宽度仅支持数字、px 或 %，例如 600px、80%")


def infer_form_type(field_name: str, py_type: str) -> str:
    """根据字段名与 Python 类型推断默认表单控件（界面与生成代码共用）。"""
    lowered = field_name.lower()
    if py_type == "bool" or "status" in lowered:
        return "BOOLEAN_SELECT"
    if py_type == "date" or "date" in lowered:
        return "DATE"
    if py_type in ("datetime", "time") or "time" in lowered:
        return "DATE_TIME"
    if any(k in lowered for k in ("remark", "desc", "content")):
        return "TEXT_AREA"
    if py_type in ("float", "int", "Decimal"):
        return "INPUT_NUMBER"
    return "INPUT"


def infer_query_type(form_type: str, py_type: str) -> str:
    """根据表单控件与 Python 类型推断默认查询方式。

    日期类字段默认使用 BETWEEN：前端日期范围控件提交数组，
    与后端 ``between`` 条件一一对应，避免范围值被当作等值条件解析。
    """
    if form_type in ("DATE", "DATE_TIME"):
        return "BETWEEN"
    if py_type == "str":
        return "LIKE"
    return "EQ"


def default_field_options(
    column_name: str, field_name: str, py_type: str, is_pk: bool, is_nullable: bool
) -> dict:
    """字段默认配置。

    配置界面（``get_gen_config``）与代码生成（``_build_field_meta``）共用本实现，
    否则界面展示的默认值与真正生成的结果会不一致。
    """
    business = not is_pk and column_name not in _NON_BUSINESS_COLUMNS
    form_type = infer_form_type(field_name, py_type)
    return {
        "form_type_name": form_type,
        "query_type_name": infer_query_type(form_type, py_type),
        "is_show_in_list": 1 if business else 0,
        "is_show_in_create": 1 if business else 0,
        "is_show_in_update": 1 if business else 0,
        "is_show_in_query": 1 if business else 0,
        "is_required": 1 if business and not is_nullable else 0,
    }


def vo_default_literal(py_type: str, is_nullable: bool) -> tuple[str, bool]:
    """返回 VO 字段的默认值字面量与是否需要 ``| None`` 标注。

    非空标量给出类型安全的零值，其余类型保持 ``None``，避免出现
    ``price: Decimal = Field(default=None)`` 这类注解与默认值互相矛盾的写法。
    """
    if is_nullable:
        return "None", True
    if py_type == "str":
        return '""', False
    if py_type == "int":
        return "0", False
    if py_type == "float":
        return "0", False
    if py_type == "bool":
        return "False", False
    return "None", True


def query_schema_type(py_type: str, query_type: str) -> str:
    """查询参数的类型标注：范围查询接受数组，IN 查询接受列表。"""
    if query_type == "BETWEEN":
        return f"list[{py_type}] | {py_type} | None"
    if query_type == "IN":
        return f"list[{py_type}] | None"
    return f"{py_type} | None"


def table_base_name(table_name: str, prefix: str | None) -> str:
    """按「移除表前缀」配置得到实体基础名。"""
    if prefix and table_name.startswith(prefix) and len(table_name) > len(prefix):
        return table_name[len(prefix) :]
    return table_name


# ── 生成代码的行级排版 ──
#
# 生成结果要求可直接通过 ruff（E302 空行、E501 行宽、I001 导入顺序），
# 而 Jinja 块标签会吞掉紧随其后的换行，模板里拼装这些行很容易出错。
# 因此字段定义行与 import 行统一在这里生成，模板只负责逐行输出。

_LINE_LIMIT = 118  # ruff line-length=120，留出余量


def build_import_lines(groups: list[list[str]]) -> list[str]:
    """按 isort 分组拼装 import 行，组间插入一个空行。"""
    lines: list[str] = []
    for group in groups:
        if not group:
            continue
        if lines:
            lines.append("")
        lines.extend(group)
    return lines


def format_from_import(module: str, names: list[str]) -> list[str]:
    """生成 from ... import ...；超长时自动换行，避免 E501。"""
    single = f"from {module} import {', '.join(names)}"
    if len(single) <= _LINE_LIMIT:
        return [single]
    return [f"from {module} import (", *(f"    {name}," for name in names), ")"]


def sort_import_entries(entries: list[list[str]]) -> list[str]:
    """按模块名对一个 import 分组内的条目排序（isort 按模块字母序排列）。"""
    ordered = sorted(entries, key=lambda entry: entry[0].removeprefix("from ").split(" import")[0])
    return [line for entry in ordered for line in entry]


def format_model_field(meta: dict) -> list[str]:
    """生成一行 SQLAlchemy mapped_column 定义，超长时换行。"""
    annotation = f"{meta['py_type']} | None" if meta["is_nullable"] else meta["py_type"]
    args = [meta["sa_column"]]
    if meta["column_name_arg"]:
        args.append(f'name="{meta["column_name"]}"')
    args.append(f'comment="{meta["field_comment"]}"')
    head = f"    {meta['model_name']}: Mapped[{annotation}] = mapped_column("
    single = f"{head}{', '.join(args)})"
    if len(single) <= _LINE_LIMIT:
        return [single]
    return [head, *(f"        {arg}," for arg in args), "    )"]


def format_pydantic_field(name: str, annotation: str, args: list[str]) -> list[str]:
    """生成一行 pydantic Field 定义，超长时换行。"""
    head = f"    {name}: {annotation} = Field("
    single = f"{head}{', '.join(args)})"
    if len(single) <= _LINE_LIMIT:
        return [single]
    return [head, *(f"        {arg}," for arg in args), "    )"]


def field_args(
    *,
    required: bool,
    is_str: bool,
    alias: str | None,
    description: str,
    default: str = "None",
) -> list[str]:
    """拼装 Field(...) 的位置参数。"""
    args = ["..." if required else f"default={default}"]
    if required and is_str:
        args.append("min_length=1")
    if alias:
        args.append(f'validation_alias="{alias}"')
    args.append(f'description="{description}"')
    return args


# ═══════════════════════════════════════════════════════════
# Jinja2 环境
# ═══════════════════════════════════════════════════════════


def _jinja_env() -> Environment:
    """前端模板使用 [[ ]] 分隔符避免 Vue {{ }} 冲突。"""
    env = Environment(  # noqa: S701 - 生成源码，不能对模板内容执行 HTML 转义
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        variable_start_string="[[",
        variable_end_string="]]",
        block_start_string="{%",
        block_end_string="%}",
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    # 字面量 "[" 不能直接写在变量分隔符前面（"[[[x]]" 会被当成变量起始），
    # 需要输出列表字面量时统一使用 [[ lb ]]
    env.globals["lb"] = "["
    return env


# ═══════════════════════════════════════════════════════════
# Service
# ═══════════════════════════════════════════════════════════


class CodegenService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── 表列表 ──

    async def get_table_page(self, query: TableQuery) -> dict:
        where = [
            "t.table_schema = current_schema()",
            "t.table_type = 'BASE TABLE'",
            "t.table_name NOT IN ('gen_table', 'gen_table_column', 'alembic_version')",
        ]
        params: dict = {"limit": query.page_size, "offset": (query.page_num - 1) * query.page_size}

        if query.keywords:
            where.append("t.table_name ILIKE :kw")
            params["kw"] = f"%{query.keywords}%"

        w = " AND ".join(where)

        total_sql = f"SELECT COUNT(*) FROM information_schema.tables t WHERE {w}"  # noqa: S608
        total = (await self.db.execute(text(total_sql), params)).scalar() or 0

        list_sql = f"""
            SELECT t.table_name,
                   obj_description(('"' || t.table_name || '"')::regclass) AS table_comment,
                   gt.update_time AS config_time
            FROM information_schema.tables t
            LEFT JOIN gen_table gt ON gt.table_name = t.table_name AND gt.is_deleted = 0
            WHERE {w}
            ORDER BY t.table_name LIMIT :limit OFFSET :offset
        """  # noqa: S608
        rows = (await self.db.execute(text(list_sql), params)).all()

        records = [
            TableVO(
                tableName=r.table_name,
                tableComment=r.table_comment or "",
                engine="PostgreSQL",
                tableCollation="数据库默认",
                # PostgreSQL information_schema 不提供表创建时间，避免返回伪造时间。
                createTime=None,
                configTime=r.config_time.strftime("%Y-%m-%d %H:%M:%S") if r.config_time else None,
                isConfigured=1 if r.config_time else 0,
            ).model_dump(by_alias=True)
            for r in rows
        ]
        return {"list": records, "total": total}

    # ── 列元数据 ──

    async def _get_columns(self, table_name: str) -> list[dict]:
        sql = """
            SELECT c.column_name, c.udt_name, c.data_type, c.is_nullable,
                   c.character_maximum_length, c.numeric_precision, c.numeric_scale,
                   pg_catalog.col_description(
                       ('"' || c.table_schema || '"."' || c.table_name || '"')::regclass::oid,
                       c.ordinal_position
                   ) AS column_comment,
                   CASE WHEN pk.column_name IS NOT NULL THEN 'PRI' ELSE '' END AS column_key
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                 AND tc.table_name = kcu.table_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND tc.table_name = :tn AND tc.table_schema = current_schema()
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_name = :tn AND c.table_schema = current_schema()
            ORDER BY c.ordinal_position
        """
        rows = await self.db.execute(text(sql), {"tn": table_name})
        cols = [
            {
                "name": r.column_name,
                "udt": r.udt_name,
                "data_type": r.data_type,
                "is_nullable": (r.is_nullable or "").upper() == "YES",
                "max_length": r.character_maximum_length,
                "precision": r.numeric_precision,
                "scale": r.numeric_scale,
                "comment": sanitize_text(r.column_comment),
                "is_pk": r.column_key == "PRI",
            }
            for r in rows
        ]
        if not cols:
            raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg=f"表 {table_name} 不存在或无字段")
        if not any(c["is_pk"] for c in cols):
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"表 {table_name} 未检测到主键，生成的 ORM 模型无法定位唯一记录",
            )
        return cols

    async def _load_saved_config(self, table_name: str) -> tuple[GenTable | None, dict[str, GenTableColumn]]:
        """读取已保存的表配置与字段配置。"""
        gt = (
            await self.db.execute(
                select(GenTable).where(GenTable.table_name == table_name, GenTable.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if gt is None:
            return None, {}
        rows = (
            (
                await self.db.execute(
                    select(GenTableColumn)
                    .where(GenTableColumn.table_id == gt.id)
                    .order_by(GenTableColumn.field_sort)
                )
            )
            .scalars()
            .all()
        )
        return gt, {sc.column_name: sc for sc in rows if sc.column_name}

    # ── 字段元数据 ──

    def _build_field_meta(self, col: dict, saved_col: GenTableColumn | None = None) -> dict:
        """把数据库列 + 已保存配置合并为模板可直接使用的字段元数据。"""
        column_name = col["name"]
        inferred_py = pg_to_python(col["udt"])
        field_name = (saved_col.field_name if saved_col and saved_col.field_name else None) or snake_to_camel(
            column_name
        )
        if not is_valid_identifier(field_name):
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"字段名 {field_name} 不是有效的代码标识符",
            )

        py_type = (saved_col.field_type if saved_col and saved_col.field_type else None) or inferred_py
        if py_type not in _TS_TYPE:
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"字段 {column_name} 的 Python 类型 {py_type} 不受支持，可选：{', '.join(_TS_TYPE)}",
            )

        ts_type = (saved_col.frontend_type if saved_col and saved_col.frontend_type else None) or py_to_ts(py_type)
        if ts_type not in _FRONTEND_TYPES:
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"字段 {column_name} 的前端类型 {ts_type} 不受支持，可选：{', '.join(sorted(_FRONTEND_TYPES))}",
            )

        # 模型属性优先与列名同名（项目 ORM 约定）；列名不是合法标识符时退回用户配置的字段名
        model_name = column_name if is_valid_identifier(column_name) else field_name
        if not is_valid_identifier(model_name):
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"列名 {column_name} 无法作为 Python 属性名，请在字段列表为其指定字段命名",
            )

        defaults = default_field_options(column_name, field_name, py_type, col["is_pk"], col["is_nullable"])
        if saved_col is not None:
            form_type_name_value = (
                form_type_name(saved_col.form_type) if saved_col.form_type else defaults["form_type_name"]
            )
            query_type_name_value = (
                query_type_name(saved_col.query_type) if saved_col.query_type else defaults["query_type_name"]
            )
            visibility = lambda value, fallback: fallback if value is None else value != 0  # noqa: E731
            is_show_in_create = visibility(saved_col.is_show_in_create, bool(defaults["is_show_in_create"]))
            is_show_in_update = visibility(saved_col.is_show_in_update, bool(defaults["is_show_in_update"]))
            show_in_list = visibility(saved_col.is_show_in_list, bool(defaults["is_show_in_list"]))
            show_in_query = visibility(saved_col.is_show_in_query, bool(defaults["is_show_in_query"]))
            required = (saved_col.is_required or 0) == 1
        else:
            form_type_name_value = defaults["form_type_name"]
            query_type_name_value = defaults["query_type_name"]
            is_show_in_create = bool(defaults["is_show_in_create"])
            is_show_in_update = bool(defaults["is_show_in_update"])
            show_in_list = bool(defaults["is_show_in_list"])
            show_in_query = bool(defaults["is_show_in_query"])
            required = bool(defaults["is_required"])

        # 主键与审计列不允许出现在新增/修改表单，避免客户端改写系统字段
        editable = column_name not in _NON_BUSINESS_COLUMNS and not col["is_pk"]
        is_show_in_create = is_show_in_create and editable
        is_show_in_update = is_show_in_update and editable

        form_control = _FORM_CONTROL.get(form_type_name_value, "input")
        query_control = _QUERY_CONTROL.get(form_control, "input")
        dict_type = sanitize_text(saved_col.dict_type) if saved_col and saved_col.dict_type else ""
        if form_control in ("select", "dict-select") and dict_type:
            form_control = "dict-select"
        if query_control in ("select", "dict-select") and dict_type:
            query_control = "dict-select"
        if form_control == "hidden":
            # 隐藏字段不参与表单与提交，避免生成 <el-input type="hidden"> 这类无效写法
            is_show_in_create = False
            is_show_in_update = False

        field_comment = sanitize_text(saved_col.field_comment, col["comment"]) if saved_col else col["comment"]
        field_comment = field_comment or field_name
        list_name = (sanitize_text(saved_col.list_name) if saved_col else "") or field_comment
        query_name = (sanitize_text(saved_col.query_name) if saved_col else "") or field_comment
        is_select_like = query_control in _SELECT_LIKE_CONTROLS
        vo_default, vo_optional = vo_default_literal(py_type, col["is_nullable"])

        # ── 前端模板派生值 ──
        if query_type_name_value == "BETWEEN":
            ts_query_type = f"[{ts_type}, {ts_type}]"
        elif query_type_name_value == "IN":
            ts_query_type = f"{ts_type}[]" if ts_type in ("string", "number", "boolean") else "string"
        else:
            ts_query_type = ts_type

        date_format = None
        if form_type_name_value == "DATE":
            date_format = "YYYY-MM-DD"
        elif form_type_name_value == "DATE_TIME":
            date_format = "YYYY-MM-DD HH:mm:ss"

        curd_modal_type = _CURD_MODAL_TYPE.get(form_control, "input")
        curd_col_templet = "custom" if dict_type else ("date" if date_format else None)
        # 状态类字段用项目约定的是否语义（启用/禁用），其余布尔字段用 是/否
        status_like = "status" in field_name.lower()
        true_label = "启用" if status_like else "是"
        false_label = "禁用" if status_like else "否"

        return {
            "column_name": column_name,
            "field_name": field_name,
            "model_name": model_name,
            # 模型属性与列名不一致时需要显式 name=；字段名与模型属性不一致时需要 validation_alias
            "column_name_arg": model_name != column_name,
            "validation_alias": model_name if field_name != model_name else None,
            "py_type": py_type,
            "ts_type": ts_type,
            "sa_column": sa_column_spec(col["udt"], col.get("max_length"), col.get("precision"), col.get("scale")),
            "sa_type_name": sa_type_name(col["udt"]),
            "field_comment": field_comment,
            "list_name": list_name,
            "query_name": query_name,
            "list_width": saved_col.list_width if saved_col and saved_col.list_width else None,
            "list_ellipsis": saved_col.list_ellipsis != 0 if saved_col else True,
            "is_pk": col["is_pk"],
            "is_nullable": col["is_nullable"],
            "is_required": required,
            "is_business": column_name not in _NON_BUSINESS_COLUMNS and not col["is_pk"],
            "is_show_in_list": show_in_list,
            "is_show_in_form": is_show_in_create or is_show_in_update,
            "is_show_in_create": is_show_in_create,
            "is_show_in_update": is_show_in_update,
            "is_show_in_query": show_in_query,
            "form_type_name": form_type_name_value,
            "query_type_name": query_type_name_value,
            "form_control": form_control,
            "query_control": query_control,
            "required_trigger": "change" if is_select_like else "blur",
            "required_action": "请选择" if is_select_like else "请输入",
            "dict_type": dict_type,
            "max_length": saved_col.max_length if saved_col and saved_col.max_length else col.get("max_length"),
            # 查询参数需要接受多值（BETWEEN 范围 / IN 列表）时使用 list[str] | str
            "query_multi_value": query_type_name_value in ("BETWEEN", "IN"),
            "query_schema_type": query_schema_type(py_type, query_type_name_value),
            "vo_default": vo_default,
            "vo_optional": vo_optional,
            "ts_query_type": ts_query_type,
            "date_format": date_format,
            "is_date_like": date_format is not None,
            "is_hidden": form_control == "hidden",
            "curd_search_type": _CURD_SEARCH_TYPE.get(query_control),
            "curd_modal_type": curd_modal_type,
            "curd_col_templet": curd_col_templet,
            "slot_name": field_name,
            "true_label": true_label,
            "false_label": false_label,
        }

    # ── 模板上下文构造 ──

    async def _build_template_context(self, table_name: str) -> dict:
        raw_cols = await self._get_columns(table_name)
        gt, saved_cols = await self._load_saved_config(table_name)

        column_names = {c["name"] for c in raw_cols}
        # 基础模型 Mixin 已经声明过的列，模型模板必须跳过（重复声明会 DuplicateColumnError）
        use_timestamp_mixin = set(_TIMESTAMP_COLUMNS) <= column_names
        use_soft_delete_mixin = _SOFT_DELETE_COLUMN in column_names
        mixin_columns = {_ID_COLUMN}
        if use_timestamp_mixin:
            mixin_columns.update(_TIMESTAMP_COLUMNS)
        if use_soft_delete_mixin:
            mixin_columns.add(_SOFT_DELETE_COLUMN)

        prefix = gt.remove_table_prefix if gt else None
        default_entity = pascal_case(table_base_name(table_name, prefix))
        entity_name = (gt.entity_name if gt and gt.entity_name else "") or default_entity
        module_name = (gt.module_name if gt and gt.module_name else "") or (
            table_name.split("_")[0] if "_" in table_name else "app"
        )
        for key, value in (("module_name", module_name), ("entity_name", entity_name)):
            if not is_valid_identifier(value):
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL,
                    msg=f"{key} {value} 不是有效的代码标识符",
                )

        entity_snake = to_snake(entity_name) or entity_name.lower()
        if not is_valid_identifier(entity_snake):
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg=f"实体名 {entity_name} 无法转换为合法的目录名，请调整实体名",
            )

        form_enabled = gt.form_enabled != 0 if gt else True
        delete_enabled = gt.delete_enabled != 0 if gt else True
        requested_delete_mode = (
            gt.delete_mode if gt and gt.delete_mode in {"logical", "physical"} else "logical"
        )
        delete_mode = requested_delete_mode
        notes: list[str] = []
        if requested_delete_mode == "logical" and not use_soft_delete_mixin:
            delete_mode = "physical"
            notes.append(f"表 {table_name} 不存在 is_deleted 列，已按「物理删除」生成，请确认删除配置。")

        business_name = sanitize_text(gt.business_name if gt else "", entity_name)
        author = sanitize_text(gt.author if gt else "", "youlai-fastapi")

        ctx: dict = {
            "table_name": table_name,
            "table_comment": sanitize_text(next((c["comment"] for c in raw_cols), ""), business_name),
            "entity_name": entity_name,
            "entity_snake": entity_snake,
            "entity_lower": lower_first(entity_name),
            "entity_kebab": entity_snake.replace("_", "-"),
            "entity_upper_snake": entity_snake.upper(),
            "module_name": module_name,
            "package_name": sanitize_text(gt.package_name if gt else "", "com.youlai.fastapi"),
            "author": author,
            "business_name": business_name,
            "entity_comment": business_name,
            "pk_name": _ID_COLUMN,
            # 权限标识前缀：{模块}:{实体短横线}，与 sys_menu.perm 及前端 v-hasPerm 完全一致
            "perm_prefix": f"{module_name}:{entity_snake.replace('_', '-')}",
            "notes": notes,
            "form_enabled": form_enabled,
            "form_layout": gt.form_layout if gt and gt.form_layout in {"dialog", "drawer"} else "dialog",
            "form_width": normalize_form_width(gt.form_width) if gt else "600px",
            "form_columns": gt.form_columns if gt and gt.form_columns in {1, 2, 3, 4} else 2,
            "delete_enabled": delete_enabled,
            "delete_mode": delete_mode,
            "delete_type": (
                gt.delete_type if gt and gt.delete_type in {"single_batch", "single", "batch"} else "single_batch"
            ),
            "parent_menu_id": gt.parent_menu_id if gt else None,
            "page_type": gt.page_type if gt and gt.page_type in {"classic", "curd"} else "classic",
            "use_timestamp_mixin": use_timestamp_mixin,
            "use_soft_delete_mixin": use_soft_delete_mixin,
            "soft_delete_filter": use_soft_delete_mixin,
            "has_decimal": False,
            "sa_imports": set(),
            "columns": [],
        }
        ctx["form_span"] = 24 // ctx["form_columns"]

        for col in raw_cols:
            meta = self._build_field_meta(col, saved_cols.get(col["name"]))
            meta["is_model_column"] = col["name"] not in mixin_columns
            ctx["columns"].append(meta)
            if meta["is_model_column"]:
                ctx["sa_imports"].add(meta["sa_type_name"])
                if meta["py_type"] == "Decimal":
                    ctx["has_decimal"] = True

        ctx["sa_imports"] = sorted(ctx["sa_imports"])
        # 模板中对 import 名称做拼接会导致行尾紧跟 Jinja 块标签（会吞掉换行），
        # 因此这里统一在 Python 侧拼好导入清单
        ctx["sqlalchemy_imports"] = ", ".join(
            name
            for name, enabled in (
                ("delete", delete_enabled and delete_mode == "physical"),
                ("func", True),
                ("select", True),
                ("update", delete_enabled and delete_mode == "logical"),
            )
            if enabled
        )
        ctx["model_date_time_imports"] = [
            name
            for name, py_type in (("date", "date"), ("datetime", "datetime"), ("time", "time"))
            if any(c["py_type"] == py_type and c["is_model_column"] for c in ctx["columns"])
        ]
        ctx["create_columns"] = [c for c in ctx["columns"] if c["is_show_in_create"]]
        ctx["update_columns"] = [c for c in ctx["columns"] if c["is_show_in_update"]]
        ctx["query_columns"] = [c for c in ctx["columns"] if c["is_show_in_query"] and c["query_control"] != "none"]
        ctx["list_columns"] = [c for c in ctx["columns"] if c["is_show_in_list"]]
        ctx["form_columns_config"] = [c for c in ctx["columns"] if c["is_show_in_form"]]
        ctx["model_columns"] = [c for c in ctx["columns"] if c["is_model_column"]]
        # VO 覆盖列表/表单/查询用到的字段，并带上 create_time / update_time 供前端按需展示
        ctx["vo_columns"] = [
            c
            for c in ctx["columns"]
            if not c["is_pk"]
            and c["column_name"] != _SOFT_DELETE_COLUMN
            and (c["is_model_column"] or c["column_name"] in _TIMESTAMP_COLUMNS)
        ]

        # Schemas 中真正用到的 Python 类型，避免生成未使用的 import（ruff F401）
        schema_types = {c["py_type"] for c in ctx["query_columns"]}
        schema_types.update(c["py_type"] for c in ctx["vo_columns"])
        if form_enabled:
            schema_types.update(c["py_type"] for c in ctx["create_columns"])
            schema_types.update(c["py_type"] for c in ctx["update_columns"])
        ctx["schema_py_types"] = schema_types
        ctx["date_time_imports"] = [name for name in ("date", "datetime", "time") if name in schema_types]
        ctx["has_list_date"] = any(c["is_date_like"] for c in ctx["list_columns"])

        # ── 逐行输出用的定义行 / 导入行（见模块内排版说明）──
        module_path = f"app.{module_name}.{entity_snake}"
        base_classes = ["Base", "BaseIdMixin"]
        if use_timestamp_mixin:
            base_classes.append("TimestampMixin")
        if use_soft_delete_mixin:
            base_classes.append("SoftDeleteMixin")
        ctx["base_classes"] = ", ".join(base_classes)
        # 菜单 SQL 里的字符串字面量：去掉会破坏 '' 引号与 $$ 块的值
        ctx["business_name_sql"] = business_name.replace("$", "").replace("'", "''")
        ctx["app_search_column"] = next(
            (c for c in ctx["query_columns"] if c["query_type_name"] == "LIKE"), None
        )
        # CURD 工具栏与行操作按钮，拼成单行数组字面量
        ctx["curd_toolbar"] = ", ".join(
            name
            for name, enabled in (
                ('"add"', form_enabled),
                ('"delete"', delete_enabled and ctx["delete_type"] in ("single_batch", "batch")),
            )
            if enabled
        )
        ctx["curd_operat"] = ", ".join(
            name
            for name, enabled in (
                ('"edit"', form_enabled),
                ('"delete"', delete_enabled and ctx["delete_type"] != "batch"),
            )
            if enabled
        )
        ctx["model_field_lines"] = [
            line for c in ctx["model_columns"] for line in format_model_field(c)
        ]
        ctx["query_field_lines"] = [
            line
            for c in ctx["query_columns"]
            for line in format_pydantic_field(
                c["field_name"],
                c["query_schema_type"],
                field_args(
                    required=False, is_str=False, alias=c["validation_alias"], description=c["field_comment"]
                ),
            )
        ]
        ctx["create_field_lines"] = [
            line
            for c in ctx["create_columns"]
            for line in format_pydantic_field(
                c["field_name"],
                c["py_type"] if c["is_required"] else f"{c['py_type']} | None",
                field_args(
                    required=c["is_required"],
                    is_str=c["py_type"] == "str",
                    alias=c["validation_alias"],
                    description=c["field_comment"],
                ),
            )
        ]
        ctx["update_field_lines"] = [
            line
            for c in ctx["update_columns"]
            for line in format_pydantic_field(
                c["field_name"],
                f"{c['py_type']} | None",
                field_args(
                    required=False, is_str=False, alias=c["validation_alias"], description=c["field_comment"]
                ),
            )
        ]
        ctx["vo_field_lines"] = [
            line
            for c in ctx["vo_columns"]
            for line in format_pydantic_field(
                c["field_name"],
                f"{c['py_type']} | None" if c["vo_optional"] else c["py_type"],
                field_args(
                    required=False,
                    is_str=False,
                    alias=c["validation_alias"],
                    description=c["field_comment"],
                    default=c["vo_default"],
                ),
            )
        ]

        model_stdlib: list[str] = []
        if ctx["model_date_time_imports"]:
            model_stdlib.append(f"from datetime import {', '.join(ctx['model_date_time_imports'])}")
        if ctx["has_decimal"]:
            model_stdlib.append("from decimal import Decimal")
        model_third_party: list[str] = []
        if ctx["model_columns"]:
            model_third_party = [
                f"from sqlalchemy import {', '.join(ctx['sa_imports'])}",
                "from sqlalchemy.orm import Mapped, mapped_column",
            ]
        ctx["model_import_lines"] = build_import_lines(
            [model_stdlib, model_third_party, [f"from app.database import {', '.join(sorted(base_classes))}"]]
        )

        schema_stdlib: list[str] = []
        if ctx["date_time_imports"]:
            schema_stdlib.append(f"from datetime import {', '.join(ctx['date_time_imports'])}")
        if "Decimal" in schema_types:
            schema_stdlib.append("from decimal import Decimal")
        ctx["schema_import_lines"] = build_import_lines(
            [
                schema_stdlib,
                ["from pydantic import BaseModel, Field"],
                ["from app.serializers import BigId"],
            ]
        )

        service_third_party = [
            f"from sqlalchemy import {ctx['sqlalchemy_imports']}",
            "from sqlalchemy.ext.asyncio import AsyncSession",
        ]
        service_schema_names = ["Create", "QueryParams", "Update", "VO"] if form_enabled else ["QueryParams", "VO"]
        service_first_party = [
            format_from_import(f"{module_path}.models", [entity_name]),
            format_from_import(
                f"{module_path}.schemas", [f"{entity_name}{suffix}" for suffix in service_schema_names]
            ),
            ["from app.exceptions import BusinessException"],
            ["from app.pagination import PageResult"],
            ["from app.response import ResultCode"],
        ]
        if delete_enabled:
            service_first_party.append(["from app.validation import parse_ids"])
        ctx["service_import_lines"] = build_import_lines(
            [service_third_party, sort_import_entries(service_first_party)]
        )

        router_third_party = [
            "from fastapi import APIRouter, Depends, Query",
            "from sqlalchemy.ext.asyncio import AsyncSession",
        ]
        router_schema_names = ["Create", "QueryParams", "Update"] if form_enabled else ["QueryParams"]
        router_first_party = [
            ["from app.database import get_db"],
            format_from_import(
                f"{module_path}.schemas", [f"{entity_name}{suffix}" for suffix in router_schema_names]
            ),
            format_from_import(f"{module_path}.service", [f"{entity_name}Service"]),
            ["from app.dependencies import get_current_user, require_perm"],
            ["from app.response import Result"],
        ]
        ctx["router_import_lines"] = build_import_lines(
            [router_third_party, sort_import_entries(router_first_party)]
        )
        return ctx

    # ── 配置 CRUD ──

    async def get_gen_config(self, table_name: str) -> GenConfigVO:
        raw_cols = await self._get_columns(table_name)
        gt, saved_cols = await self._load_saved_config(table_name)

        field_configs = []
        for col in raw_cols:
            sc = saved_cols.get(col["name"])
            py_type = (sc.field_type if sc and sc.field_type else None) or pg_to_python(col["udt"])
            field_name = (sc.field_name if sc and sc.field_name else None) or snake_to_camel(col["name"])
            ts_type = (sc.frontend_type if sc and sc.frontend_type else None) or py_to_ts(py_type)
            defaults = default_field_options(col["name"], field_name, py_type, col["is_pk"], col["is_nullable"])
            form_type = form_type_name(sc.form_type) if sc and sc.form_type else defaults["form_type_name"]
            query_type = query_type_name(sc.query_type) if sc and sc.query_type else defaults["query_type_name"]

            field_configs.append(
                FieldConfigVO(
                    columnName=col["name"],
                    columnType=col["udt"],
                    columnComment=col["comment"],
                    fieldComment=(sanitize_text(sc.field_comment) if sc and sc.field_comment else "") or col["comment"],
                    queryName=(sanitize_text(sc.query_name) if sc and sc.query_name else "") or col["comment"],
                    listName=(sanitize_text(sc.list_name) if sc and sc.list_name else "") or col["comment"],
                    listWidth=sc.list_width if sc else None,
                    listEllipsis=sc.list_ellipsis if sc else 1,
                    isNullable="YES" if col["is_nullable"] else "NO",
                    isPk=col["is_pk"],
                    columnKey="PRI" if col["is_pk"] else "",
                    fieldName=field_name,
                    fieldType=py_type,
                    frontendType=ts_type,
                    tsType=ts_type,
                    isShowInList=(
                        (sc.is_show_in_list or 0)
                        if sc and sc.is_show_in_list is not None
                        else defaults["is_show_in_list"]
                    ),
                    isShowInForm=(
                        1
                        if (
                            (sc.is_show_in_create if sc and sc.is_show_in_create is not None else 0)
                            or (sc.is_show_in_update if sc and sc.is_show_in_update is not None else 0)
                        )
                        else (1 if sc and sc.is_show_in_form else 0)
                    )
                    if sc
                    else defaults["is_show_in_create"],
                    isShowInCreate=(
                        (sc.is_show_in_create or 0) if sc and sc.is_show_in_create is not None else 0
                    )
                    if sc
                    else defaults["is_show_in_create"],
                    isShowInUpdate=(
                        (sc.is_show_in_update or 0) if sc and sc.is_show_in_update is not None else 0
                    )
                    if sc
                    else defaults["is_show_in_update"],
                    isShowInQuery=(
                        (sc.is_show_in_query or 0) if sc and sc.is_show_in_query is not None else 0
                    )
                    if sc
                    else defaults["is_show_in_query"],
                    isRequired=(
                        (sc.is_required or 0)
                        if sc and sc.is_required is not None
                        else defaults["is_required"]
                    ),
                    formType=_FORM_TYPE.get(form_type, _FORM_TYPE["INPUT"]),
                    queryType=_QUERY_TYPE.get(query_type, _QUERY_TYPE["EQ"]),
                    dictType=sanitize_text(sc.dict_type) if sc and sc.dict_type else None,
                    maxLength=(sc.max_length if sc and sc.max_length else col.get("max_length")),
                    fieldSort=sc.field_sort if sc else None,
                )
            )

        prefix = gt.remove_table_prefix if gt else None
        default_business = pascal_case(table_base_name(table_name, prefix))
        return GenConfigVO(
            id=gt.id if gt else None,
            tableName=table_name,
            businessName=sanitize_text(gt.business_name if gt else "", default_business),
            moduleName=gt.module_name if gt else (table_name.split("_")[0] if "_" in table_name else "app"),
            packageName=gt.package_name if gt else "com.youlai.fastapi",
            entityName=gt.entity_name if gt else default_business,
            author=gt.author if gt else "youlai-fastapi",
            parentMenuId=gt.parent_menu_id if gt else None,
            pageType=gt.page_type if gt and gt.page_type in {"classic", "curd"} else "classic",
            formEnabled=gt.form_enabled if gt else 1,
            formLayout=gt.form_layout if gt else "dialog",
            formWidth=gt.form_width if gt else "600px",
            formColumns=gt.form_columns if gt else 2,
            deleteEnabled=gt.delete_enabled if gt else 1,
            deleteMode=gt.delete_mode if gt else "logical",
            deleteType=gt.delete_type if gt else "single_batch",
            removeTablePrefix=prefix,
            fieldConfigs=field_configs,
        )

    @staticmethod
    def _validate_field_configs(form: GenConfigForm) -> None:
        """保存前校验字段配置，让界面即时得到错误而不是等到生成时才失败。"""
        for fc in form.field_configs or []:
            label = fc.column_name or fc.field_name or "字段"
            if fc.field_name and not is_valid_identifier(fc.field_name):
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL,
                    msg=f"字段 {label} 的字段名 {fc.field_name} 不是有效的代码标识符",
                )
            if fc.field_type and fc.field_type not in _TS_TYPE:
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL,
                    msg=f"字段 {label} 的 Python 类型 {fc.field_type} 不受支持",
                )
            if fc.frontend_type and fc.frontend_type not in _FRONTEND_TYPES:
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL,
                    msg=f"字段 {label} 的前端类型 {fc.frontend_type} 不受支持",
                )
            if fc.form_type is not None and fc.form_type not in _FORM_TYPE_REV:
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL, msg=f"字段 {label} 的表单类型取值非法"
                )
            if fc.query_type is not None and fc.query_type not in _QUERY_TYPE_REV:
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL, msg=f"字段 {label} 的查询类型取值非法"
                )

    async def save_gen_config(self, table_name: str, form: GenConfigForm) -> None:
        self._validate_field_configs(form)
        gt, _ = await self._load_saved_config(table_name)

        entity_name = form.entity_name or pascal_case(table_base_name(table_name, form.remove_table_prefix))
        module_name = form.module_name or (table_name.split("_")[0] if "_" in table_name else "app")
        for key, value in (("module_name", module_name), ("entity_name", entity_name)):
            if not is_valid_identifier(value):
                raise BusinessException(
                    code=ResultCode.PARAM_VALID_FAIL,
                    msg=f"{key} {value} 不是有效的代码标识符",
                )

        values = {
            "table_name": table_name,
            "module_name": module_name,
            "package_name": form.package_name or "com.youlai.fastapi",
            "business_name": sanitize_text(form.business_name, entity_name),
            "entity_name": entity_name,
            "author": sanitize_text(form.author, "youlai-fastapi"),
            "parent_menu_id": form.parent_menu_id,
            "remove_table_prefix": form.remove_table_prefix,
            "page_type": form.page_type if form.page_type in {"classic", "curd"} else "classic",
            "form_enabled": form.form_enabled if form.form_enabled in {0, 1} else 1,
            "form_layout": form.form_layout if form.form_layout in {"dialog", "drawer"} else "dialog",
            "form_width": normalize_form_width(form.form_width),
            "form_columns": form.form_columns if form.form_columns in {1, 2, 3, 4} else 2,
            "delete_enabled": form.delete_enabled if form.delete_enabled in {0, 1} else 1,
            "delete_mode": form.delete_mode if form.delete_mode in {"logical", "physical"} else "logical",
            "delete_type": (
                form.delete_type if form.delete_type in {"single_batch", "single", "batch"} else "single_batch"
            ),
        }

        if gt:
            for key, value in values.items():
                setattr(gt, key, value)
            gt.update_time = datetime.now()
            await self.db.flush()
        else:
            gt = GenTable(**values)
            self.db.add(gt)
            await self.db.flush()

        # 删除旧字段配置后重建
        await self.db.execute(sa_delete(GenTableColumn).where(GenTableColumn.table_id == gt.id))

        for idx, fc in enumerate(form.field_configs or []):
            self.db.add(
                GenTableColumn(
                    table_id=gt.id,
                    column_name=fc.column_name,
                    column_type=fc.column_type,
                    field_name=fc.field_name or "",
                    field_type=fc.field_type,
                    frontend_type=fc.frontend_type,
                    field_sort=fc.field_sort if fc.field_sort is not None else idx,
                    field_comment=sanitize_text(fc.field_comment),
                    query_name=sanitize_text(fc.query_name),
                    list_name=sanitize_text(fc.list_name),
                    list_width=fc.list_width if fc.list_width and fc.list_width > 0 else None,
                    list_ellipsis=fc.list_ellipsis if fc.list_ellipsis in {0, 1} else 1,
                    is_show_in_list=fc.is_show_in_list if fc.is_show_in_list in {0, 1} else 0,
                    is_show_in_form=fc.is_show_in_form if fc.is_show_in_form in {0, 1} else 0,
                    is_show_in_create=fc.is_show_in_create if fc.is_show_in_create in {0, 1} else 0,
                    is_show_in_update=fc.is_show_in_update if fc.is_show_in_update in {0, 1} else 0,
                    is_show_in_query=fc.is_show_in_query if fc.is_show_in_query in {0, 1} else 0,
                    is_required=fc.is_required if fc.is_required in {0, 1} else 0,
                    max_length=fc.max_length,
                    form_type=fc.form_type,
                    query_type=fc.query_type,
                    dict_type=sanitize_text(fc.dict_type),
                )
            )
            await self.db.flush()

    async def delete_gen_config(self, table_name: str) -> None:
        gt = (
            await self.db.execute(
                select(GenTable).where(GenTable.table_name == table_name, GenTable.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if gt:
            await self.db.execute(sa_delete(GenTableColumn).where(GenTableColumn.table_id == gt.id))
            await self.db.delete(gt)
            await self.db.flush()

    # ── 预览 / 下载 ──

    async def preview_code(self, table_name: str, page_type: str, frontend_type: str) -> list[PreviewVO]:
        files = await self._collect_files(table_name, page_type, frontend_type)
        return [
            PreviewVO(
                path=f["path"],
                fileName=f["file_name"],
                content=f["content"],
                scope=f["scope"],
                language=f["language"],
            )
            for f in files
        ]

    async def download_code(self, table_name: str, page_type: str, frontend_type: str) -> bytes:
        files = await self._collect_files(table_name, page_type, frontend_type)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f"{f['path']}/{f['file_name']}", f["content"])
        buf.seek(0)
        return buf.read()

    async def _collect_files(self, table_name: str, page_type: str, frontend_type: str) -> list[dict]:
        self._validate_generation_options(page_type, frontend_type)
        ctx = await self._build_template_context(table_name)
        files = self._render_files(ctx, page_type, frontend_type)
        if not files:
            raise BusinessException(code=ResultCode.SYSTEM_ERROR, msg="没有可生成的代码文件")
        return files

    @staticmethod
    def _validate_generation_options(page_type: str, frontend_type: str) -> None:
        if page_type not in {"classic", "curd"}:
            raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="页面类型仅支持 classic 或 curd")
        # web 与 app 均为 TypeScript 工程（vue-tsc 类型检查），不再生成 .js 产物
        if frontend_type != "ts":
            raise BusinessException(
                code=ResultCode.PARAM_VALID_FAIL,
                msg="前端类型仅支持 ts：web/ 与 app/ 都是 TypeScript 工程",
            )

    def _render_templates(self, env: Environment, ctx: dict, specs: list[tuple], out: list[dict]) -> None:
        """渲染一组模板；任一模板失败时给出可定位的业务错误而不是 500 堆栈。"""
        for tpl, fname, path, scope in specs:
            try:
                content = env.get_template(tpl).render(**ctx)
            except Exception as exc:  # noqa: BLE001 - 统一转换为业务异常，附上模板名便于排查
                raise BusinessException(
                    code=ResultCode.SYSTEM_ERROR,
                    msg=f"渲染代码模板 {tpl} 失败: {exc}",
                ) from exc
            out.append(
                {
                    "path": path,
                    "file_name": fname,
                    "content": content,
                    "scope": scope,
                    "language": fname.rsplit(".", 1)[-1],
                }
            )

    def _render_files(self, ctx: dict, page_type: str, frontend_type: str) -> list[dict]:
        env = _jinja_env()
        out: list[dict] = []

        module = ctx["module_name"]
        snake = ctx["entity_snake"]
        kebab = ctx["entity_kebab"]
        server_path = f"server/app/{module}/{snake}"
        web_api_path = f"web/src/api/{module}/{kebab}"
        web_view_path = f"web/src/views/{module}/{kebab}"
        app_api_path = "app/src/api"
        app_view_path = f"app/src/subPages/work/{kebab}"

        # 后端
        self._render_templates(
            env,
            ctx,
            [
                ("backend/__init__.py.j2", "__init__.py", server_path, "backend"),
                ("backend/router.py.j2", "router.py", server_path, "backend"),
                ("backend/service.py.j2", "service.py", server_path, "backend"),
                ("backend/schemas.py.j2", "schemas.py", server_path, "backend"),
                ("backend/models.py.j2", "models.py", server_path, "backend"),
            ],
            out,
        )

        # 菜单初始化 SQL：仅在配置了上级菜单时生成，只产出文件、不直接写库
        if ctx["parent_menu_id"] is not None:
            self._render_templates(
                env,
                ctx,
                [("sql/menu.sql.j2", f"{snake}_menu.sql", "server/sql", "backend")],
                out,
            )

        # Web 端 API 与类型（普通页面与 CURD 封装页面共用）
        self._render_templates(
            env,
            ctx,
            [
                ("frontend/ts/api.ts.j2", "index.ts", web_api_path, "frontend"),
                ("frontend/ts/types.ts.j2", "types.ts", web_api_path, "frontend"),
            ],
            out,
        )
        if page_type == "curd":
            self._render_templates(
                env,
                ctx,
                [("frontend/ts/curd/index.vue.j2", "index.vue", web_view_path, "frontend")],
                out,
            )
            curd_configs = [
                ("frontend/ts/curd/search.ts.j2", "search.ts", f"{web_view_path}/config"),
                ("frontend/ts/curd/content.ts.j2", "content.ts", f"{web_view_path}/config"),
            ]
            if ctx["form_enabled"]:
                curd_configs += [
                    ("frontend/ts/curd/add.ts.j2", "add.ts", f"{web_view_path}/config"),
                    ("frontend/ts/curd/edit.ts.j2", "edit.ts", f"{web_view_path}/config"),
                ]
            self._render_templates(
                env,
                ctx,
                [(tpl, fname, path, "frontend") for tpl, fname, path in curd_configs],
                out,
            )
        else:
            self._render_templates(
                env,
                ctx,
                [("frontend/ts/index.vue.j2", "index.vue", web_view_path, "frontend")],
                out,
            )

        # uni-app 客户端模板，与 web 共用同一套字段和后端接口配置。
        self._render_templates(
            env,
            ctx,
            [
                ("frontend/app/api.ts.j2", f"{kebab}.ts", app_api_path, "app"),
                ("frontend/app/index.vue.j2", "index.vue", app_view_path, "app"),
            ],
            out,
        )

        return out
