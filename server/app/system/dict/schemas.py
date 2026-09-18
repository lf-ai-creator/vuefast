"""字典管理 Schemas。"""

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field

from app.serializers import BigId


class DictSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=lambda name: AliasChoices(
                name, {"dictCode": "dict_code", "tagType": "tag_type"}.get(name, name)
            )
        ),
    )


class DictQuery(BaseModel):
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    keywords: str | None = None


class DictCreate(DictSchema):
    dictCode: str = Field(..., min_length=1, max_length=50, description="类型编码")
    name: str = Field(..., min_length=1, max_length=50, description="类型名称")
    status: int = Field(default=1)
    remark: str | None = None


class DictUpdate(DictSchema):
    id: BigId
    dictCode: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=50)
    status: int = Field(default=1)
    remark: str | None = None


class DictForm(DictUpdate):
    pass


class DictItemCreate(DictSchema):
    dictCode: str | None = Field(default=None, description="关联字典编码")
    value: str = Field(..., max_length=50)
    label: str = Field(..., max_length=100)
    tagType: str | None = Field(default=None, max_length=50)
    status: int = Field(default=1)
    sort: int = Field(default=0)
    remark: str | None = None


class DictItemUpdate(DictSchema):
    id: BigId
    dictCode: str
    value: str
    label: str
    tagType: str | None = None
    status: int = Field(default=1)
    sort: int = Field(default=0)
    remark: str | None = None


class DictItemForm(DictItemUpdate):
    pass


class DictVO(DictSchema):
    id: BigId | None = None
    dictCode: str = ""
    name: str = ""
    status: int = 1
    remark: str | None = None
    createTime: str | None = None
    updateTime: str | None = None
    model_config = {"from_attributes": True}


class DictItemVO(DictSchema):
    id: BigId | None = None
    dictCode: str = ""
    value: str = ""
    label: str = ""
    tagType: str | None = None
    status: int = 1
    sort: int = 0
    remark: str | None = None
    model_config = {"from_attributes": True}


class DictItemOptionVO(DictSchema):
    value: str
    label: str
    tagType: str | None = None
    sort: int | None = None
    model_config = {"from_attributes": True}
