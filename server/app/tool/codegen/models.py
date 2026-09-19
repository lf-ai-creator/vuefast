"""代码生成配置 ORM 模型 — gen_table / gen_table_column。"""

from sqlalchemy import BigInteger, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BaseIdMixin, SoftDeleteMixin, TimestampMixin


class GenTable(Base, BaseIdMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "gen_table"

    table_name: Mapped[str] = mapped_column(String(100), unique=True, comment="表名")
    module_name: Mapped[str | None] = mapped_column(String(100), comment="模块名")
    package_name: Mapped[str] = mapped_column(String(255), comment="包名")
    business_name: Mapped[str] = mapped_column(String(100), comment="业务名")
    entity_name: Mapped[str] = mapped_column(String(100), comment="实体类名")
    author: Mapped[str] = mapped_column(String(50), comment="作者")
    parent_menu_id: Mapped[int | None] = mapped_column(BigInteger, comment="上级菜单ID")
    remove_table_prefix: Mapped[str | None] = mapped_column(String(20), comment="要移除的表前缀")
    page_type: Mapped[str | None] = mapped_column(String(20), comment="页面类型(classic/curd)")
    form_enabled: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1", comment="是否生成新增修改")
    form_layout: Mapped[str] = mapped_column(String(20), default="dialog", server_default="dialog", comment="表单布局")
    form_width: Mapped[str] = mapped_column(String(20), default="600px", server_default="600px", comment="表单宽度")
    form_columns: Mapped[int] = mapped_column(SmallInteger, default=2, server_default="2", comment="表单每行列数")
    delete_enabled: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="是否允许删除"
    )
    delete_mode: Mapped[str] = mapped_column(
        String(20), default="logical", server_default="logical", comment="删除方式"
    )
    delete_type: Mapped[str] = mapped_column(
        String(20), default="single_batch", server_default="single_batch", comment="删除类型"
    )


class GenTableColumn(Base, BaseIdMixin, TimestampMixin):
    __tablename__ = "gen_table_column"

    table_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("gen_table.id", ondelete="CASCADE"), comment="关联 gen_table.id"
    )
    column_name: Mapped[str | None] = mapped_column(String(100), comment="列名")
    column_type: Mapped[str | None] = mapped_column(String(50), comment="列类型")
    column_length: Mapped[int | None] = mapped_column(Integer, comment="列长度")
    field_name: Mapped[str] = mapped_column(String(100), comment="字段名")
    field_type: Mapped[str | None] = mapped_column(String(100), comment="字段类型")
    frontend_type: Mapped[str | None] = mapped_column(String(50), comment="前端类型")
    field_sort: Mapped[int | None] = mapped_column(Integer, comment="排序")
    field_comment: Mapped[str | None] = mapped_column(String(255), comment="注释")
    query_name: Mapped[str | None] = mapped_column(String(100), comment="查询条件名称")
    list_name: Mapped[str | None] = mapped_column(String(100), comment="列表字段名称")
    list_width: Mapped[int | None] = mapped_column(Integer, comment="列表列宽")
    list_ellipsis: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1", comment="列表自动省略")
    max_length: Mapped[int | None] = mapped_column(Integer, comment="最大长度")
    is_required: Mapped[int | None] = mapped_column(SmallInteger, comment="是否必填")
    is_show_in_list: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0", comment="列表显示")
    is_show_in_form: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0", comment="表单显示")
    is_show_in_create: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0", comment="新增显示")
    is_show_in_update: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0", comment="更新显示")
    is_show_in_query: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0", comment="查询显示")
    query_type: Mapped[int | None] = mapped_column(SmallInteger, comment="查询方式")
    form_type: Mapped[int | None] = mapped_column(SmallInteger, comment="表单类型")
    dict_type: Mapped[str | None] = mapped_column(String(50), comment="字典类型")
