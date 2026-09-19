"""代码生成 Pydantic Schemas。"""

from pydantic import BaseModel, Field

# ── 查询参数 ──


class TableQuery(BaseModel):
    page_num: int = Field(default=1, ge=1, alias="pageNum")
    page_size: int = Field(default=10, ge=1, le=100, alias="pageSize")
    keywords: str | None = None

    model_config = {"populate_by_name": True}


class PreviewQuery(BaseModel):
    """预览/下载参数（当前由路由显式声明，保留类型供内部复用）。"""

    page_type: str = Field(default="classic", alias="pageType")
    frontend_type: str = Field(default="ts", alias="type")

    model_config = {"populate_by_name": True}


# ── VO ──


class TableVO(BaseModel):
    table_name: str = Field(default="", alias="tableName")
    table_comment: str = Field(default="", alias="tableComment")
    engine: str = Field(default="", alias="engine")
    table_collation: str = Field(default="", alias="tableCollation")
    create_time: str | None = Field(default=None, alias="createTime")
    config_time: str | None = Field(default=None, alias="configTime")
    is_configured: int = Field(default=0, alias="isConfigured")

    model_config = {"populate_by_name": True}


class FieldConfigVO(BaseModel):
    column_name: str = Field(default="", alias="columnName")
    column_type: str = Field(default="", alias="columnType")
    column_comment: str = Field(default="", alias="columnComment")
    field_comment: str = Field(default="", alias="fieldComment")
    query_name: str = Field(default="", alias="queryName")
    list_name: str = Field(default="", alias="listName")
    list_width: int | None = Field(default=None, alias="listWidth")
    list_ellipsis: int = Field(default=1, alias="listEllipsis")
    is_nullable: str = Field(default="YES", alias="isNullable")
    is_pk: bool = Field(default=False, alias="isPk")
    column_key: str = Field(default="", alias="columnKey")
    field_name: str = Field(default="", alias="fieldName")
    field_type: str = Field(default="", alias="fieldType")
    frontend_type: str | None = Field(default=None, alias="frontendType")
    ts_type: str = Field(default="", alias="tsType")
    is_show_in_list: int = Field(default=0, alias="isShowInList")
    is_show_in_form: int = Field(default=0, alias="isShowInForm")
    is_show_in_create: int = Field(default=0, alias="isShowInCreate")
    is_show_in_update: int = Field(default=0, alias="isShowInUpdate")
    is_show_in_query: int = Field(default=0, alias="isShowInQuery")
    is_required: int = Field(default=0, alias="isRequired")
    form_type: int | None = Field(default=None, alias="formType")
    query_type: int | None = Field(default=None, alias="queryType")
    dict_type: str | None = Field(default=None, alias="dictType")
    max_length: int | None = Field(default=None, alias="maxLength")
    field_sort: int | None = Field(default=None, alias="fieldSort")

    model_config = {"populate_by_name": True}


class GenConfigVO(BaseModel):
    id: int | None = None
    table_name: str = Field(default="", alias="tableName")
    business_name: str | None = Field(default=None, alias="businessName")
    module_name: str | None = Field(default=None, alias="moduleName")
    package_name: str | None = Field(default=None, alias="packageName")
    entity_name: str = Field(default="", alias="entityName")
    author: str | None = Field(default=None, alias="author")
    parent_menu_id: int | None = Field(default=None, alias="parentMenuId")
    page_type: str | None = Field(default=None, alias="pageType")
    form_enabled: int = Field(default=1, alias="formEnabled")
    form_layout: str = Field(default="dialog", alias="formLayout")
    form_width: str = Field(default="600px", alias="formWidth")
    form_columns: int = Field(default=2, alias="formColumns")
    delete_enabled: int = Field(default=1, alias="deleteEnabled")
    delete_mode: str = Field(default="logical", alias="deleteMode")
    delete_type: str = Field(default="single_batch", alias="deleteType")
    remove_table_prefix: str | None = Field(default=None, alias="removeTablePrefix")
    field_configs: list[FieldConfigVO] = Field(default_factory=list, alias="fieldConfigs")

    model_config = {"populate_by_name": True}


class PreviewVO(BaseModel):
    path: str = ""
    file_name: str = Field(default="", alias="fileName")
    content: str = ""
    scope: str = ""
    language: str = ""

    model_config = {"populate_by_name": True}


# ── 请求体 ──


class FieldConfigForm(BaseModel):
    id: int | None = None
    column_name: str | None = Field(default=None, alias="columnName")
    column_type: str | None = Field(default=None, alias="columnType")
    field_name: str | None = Field(default=None, alias="fieldName")
    field_sort: int | None = Field(default=None, alias="fieldSort")
    field_type: str | None = Field(default=None, alias="fieldType")
    frontend_type: str | None = Field(default=None, alias="frontendType")
    field_comment: str | None = Field(default=None, alias="fieldComment")
    query_name: str | None = Field(default=None, alias="queryName")
    list_name: str | None = Field(default=None, alias="listName")
    list_width: int | None = Field(default=None, alias="listWidth")
    list_ellipsis: int | None = Field(default=None, alias="listEllipsis")
    is_show_in_list: int | None = Field(default=None, alias="isShowInList")
    is_show_in_form: int | None = Field(default=None, alias="isShowInForm")
    is_show_in_create: int | None = Field(default=None, alias="isShowInCreate")
    is_show_in_update: int | None = Field(default=None, alias="isShowInUpdate")
    is_show_in_query: int | None = Field(default=None, alias="isShowInQuery")
    is_required: int | None = Field(default=None, alias="isRequired")
    max_length: int | None = Field(default=None, alias="maxLength")
    form_type: int | None = Field(default=None, alias="formType")
    query_type: int | None = Field(default=None, alias="queryType")
    dict_type: str | None = Field(default=None, alias="dictType")

    model_config = {"populate_by_name": True}


class GenConfigForm(BaseModel):
    id: int | None = None
    table_name: str = Field(default="", alias="tableName")
    business_name: str | None = Field(default=None, alias="businessName")
    module_name: str | None = Field(default=None, alias="moduleName")
    package_name: str | None = Field(default=None, alias="packageName")
    entity_name: str | None = Field(default=None, alias="entityName")
    author: str | None = Field(default=None, alias="author")
    parent_menu_id: int | None = Field(default=None, alias="parentMenuId")
    page_type: str | None = Field(default=None, alias="pageType")
    form_enabled: int | None = Field(default=None, alias="formEnabled")
    form_layout: str | None = Field(default=None, alias="formLayout")
    form_width: str | None = Field(default=None, alias="formWidth")
    form_columns: int | None = Field(default=None, alias="formColumns")
    delete_enabled: int | None = Field(default=None, alias="deleteEnabled")
    delete_mode: str | None = Field(default=None, alias="deleteMode")
    delete_type: str | None = Field(default=None, alias="deleteType")
    remove_table_prefix: str | None = Field(default=None, alias="removeTablePrefix")
    field_configs: list[FieldConfigForm] | None = Field(default=None, alias="fieldConfigs")

    model_config = {"populate_by_name": True}
