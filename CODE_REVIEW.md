# 项目代码审查与修复记录

## 第二轮：代码生成功能专项评审（2026-09-19）

范围：`server/app/tool/codegen/`（服务、模板、路由）、`web/src/views/codegen/` 与 `web/src/api/codegen/`，
以及生成产物是否符合项目技术栈。评审方式：脱离数据库渲染模板，把产物写入真实工程目录做
`ruff` / `import` / `vue-tsc` / `eslint` / `stylelint` 验证后清理。

### 已修复问题

| 优先级 | 问题 | 修复结果 |
| --- | --- | --- |
| 高 | 生成的 SQLAlchemy 模型重复声明 `create_time` / `update_time` / `is_deleted`，任何含审计列的表导入即 `DuplicateColumnError` | 模型只声明非 Mixin 列；按列是否存在决定挂载 `TimestampMixin` / `SoftDeleteMixin`，无审计列的表不再强行继承 |
| 高 | 系统列默认被勾选进新增/修改表单，客户端可改写 `is_deleted`、`create_time` | 默认字段配置与 `filter` 统一排除系统列；`Create` / `Update` 不再生成这些字段，表单模板也不再渲染 |
| 高 | 逻辑删除未生效：列表、详情、更新都不过滤 `is_deleted`，删除后记录仍然可见 | 查询与详情统一追加 `is_deleted == 0`；删除改用 SQLAlchemy `update()`，不再用 f-string 拼 SQL |
| 高 | 目录命名不符合项目约定：后端包为小驼峰（`server/app/demo/demoOrderInfo`） | 后端包改为下划线目录、Web/App 改为短横线目录，`import` 与前端文件预览路径同步 |
| 高 | 非超管角色无法保存代码生成配置：路由要求 `sys:codegen:update`，初始菜单只有菜单 201、没有任何按钮权限 | 新增 alembic `20260919_06` 与初始化 SQL 补齐 `sys:codegen:list` / `sys:codegen:update` 并授权管理员角色；列表/预览/下载补上 `list` 权限 |
| 中 | 查询表单对 `BOOLEAN_SELECT` / `DICT_SELECT` / `SWITCH` / `FILE_UPLOAD` 等类型不生成控件，渲染出空的 `el-form-item` | 查询控件改由后端计算（`query_control`），覆盖全部表单类型；`HIDDEN`、文件类不再进入查询 |
| 中 | 界面默认值与生成结果不一致：`get_gen_config` 与 `_build_field_meta` 各写一套推断逻辑 | 抽出 `infer_form_type` / `infer_query_type` / `default_field_options`，界面与生成共用同一实现 |
| 中 | 用户在字段列表选择的 Python 类型、前端类型被忽略或未经校验直接进模板 | 支持并校验 `field_type` / `frontend_type`，模型属性保持列名、Schema 用 `validation_alias` 取值 |
| 中 | `varchar` 长度与 `numeric` 精度被写死为 `String(255)` / `Numeric(18, 2)` | 读取 `information_schema` 的 `character_maximum_length` / `numeric_precision` / `numeric_scale` 生成真实类型 |
| 中 | VO 的 `id` 用 `int`，前端按 `string` 处理存在大整数精度风险 | VO 改用 `app.serializers.BigId`，与项目其它模块一致 |
| 中 | 生成的后端代码不符合项目约定：相对导入、手工拼装 VO、缺少列表权限、分页返回结构不一致 | 改用绝对导入、`VO.model_validate(..., from_attributes=True)`、返回 `PageResult`、补 `:list` 权限、`pageNum`/`pageSize` 与项目一致 |
| 中 | 可配置的「页面类型 = 封装(CURD)」在后端只校验不渲染，选项形同无效 | 新增 CURD 模板：`PageSearch` / `PageContent` / `PageModal` + `config/{search,content,add,edit}.ts`，按 `pageType` 分发 |
| 中 | 「上级菜单」保存后不生成任何菜单，界面文案却声称会自动创建 | 新增 `server/sql/<表名>_menu.sql`（DO 块、按权限标识判重、业务名转义），并修正界面文案为「生成脚本 + 手动分配权限」 |
| 中 | 生成内容可注入：字段描述、业务名、作者未清理即可闭合字符串字面量或注释 | 新增 `sanitize_text`，清理 `"`、换行、`*/`、`${`；表单宽度、字段名、类型枚举全部校验 |
| 中 | `web/`、`app/` 都是 TypeScript 工程，却仍提供 `type=js` 产物模板 | 移除死模板与 js 分支，`type` 仅接受 `ts`，不合法时返回明确业务错误 |
| 低 | 必填校验统一 `blur` 触发；`HIDDEN` 渲染 `<el-input type="hidden">`；新增表单复用上次编辑残留 | 按控件类型选择 `blur`/`change` 与提示语；隐藏字段不再进表单；新增/编辑前先重置表单 |
| 低 | `author` 配置从未使用；下载 ZIP 名固定且由表名直接拼响应头 | 作者写入生成文件头部；ZIP 文件名按表名过滤为 ASCII 安全字符 |
| 低 | `PreviewQuery` 死代码、`StreamingResponse` 函数内导入、`is_configured` 依赖全表扫描 | 统一使用 `PreviewQuery` 作为查询参数依赖、导入上提；`is_configured` 直接取 `LEFT JOIN` 结果 |

### 新增能力

1. 封装(CURD)页面类型真正可用：生成 `index.vue` + `config/search.ts`、`content.ts`、`add.ts`、`edit.ts`，
   字典字段自动生成 `DictTag` / `DictSelect` 插槽，`status` 类字段使用「启用/禁用」语义。
2. 菜单初始化脚本：配置上级菜单后随代码生成 `server/sql/<表名>_menu.sql`（只生成文件，不自动写库）。
3. 生成模块 `__init__.py` 内含 `registry.py` / `main.py` 接入步骤，避免生成后忘记挂载路由。

### 验证结果

- 后端：`pytest` 154 项通过（新增 `tests/test_codegen.py` 28 项，覆盖模型可导入、系统列不进表单、
  逻辑删除过滤、字段类型覆盖、CURD/菜单产物、注入清理、LF 换行等回归点）。
- `ruff check app/tool/codegen tests/test_codegen.py`：无 I001/E501/F401；仅剩项目既有的
  `B008`（FastAPI `Query(default=...)`）与 `N803`（路径参数 `id`）风格规则。
- 生成产物端到端验证（写入真实工程后执行，验证完已清理）：
  - `ruff check app/demo`：0 个 I001/E501，仅 N815/B008/N803，与项目既有代码同类；
  - 生成模块 `models` / `schemas` / `service` / `router` 全部可导入，`create_app()` 正常；
  - Web：`pnpm type-check` 通过，ESLint 对生成文件 0 error 0 warning；
  - App：`pnpm check`（vue-tsc + ESLint + Stylelint）全部通过。
- 未验证：真实 PostgreSQL 上的元数据读取、CURD 页面与菜单 SQL 的运行时交互、本地写入（File System
  Access API）真实落盘，这些需要数据库、登录态与浏览器环境。

### 使用变化

1. 生成目录命名调整：后端为 `server/app/<module>/<table_snake>/`，Web 为
   `web/src/{api,views}/<module>/<table-kebab>/`，App 为 `app/src/api/<table-kebab>.ts` 与
   `app/src/subPages/work/<table-kebab>/`。
2. 生成的后端代码不会自动接入工程，请按模块 `__init__.py` 的说明修改 `registry.py` 与 `main.py`。
3. 需要执行 `alembic upgrade head`（或重跑初始化 SQL）以获得 `sys:codegen:*` 按钮权限，否则非超管
   角色仍会被拒绝保存配置。
4. 生成后的前端文件建议执行 `pnpm lint` / `pnpm check` 统一格式；模板已按 Prettier(100) 与
   ruff(line-length=120) 排版，常规字段下无需再手工调整。
5. 不再支持 `type=js`：`web/` 与 `app/` 均为 TypeScript 工程。

---

## 第一轮：认证、权限与系统管理评审

审查日期：2026-09-19。范围覆盖 `server/`、`web/`、`app/`，重点检查认证、权限、系统管理接口、字段映射和构建流程。

### 已修复问题

| 优先级 | 问题 | 修复结果 |
| --- | --- | --- |
| 高 | JWT 使用源码公开默认密钥 | 删除默认值，强制配置至少 32 字符密钥；本地随机密钥仅写入被忽略的 `.env`。 |
| 高 | 短信与微信占位实现可签发真实令牌 | 未接入真实验证的登录、绑定及验证码发送接口明确返回 501，不查询或创建用户。 |
| 高 | 省略验证码即可登录 | 登录表单强制验证码，验证失败返回 400，不执行密码认证；验证码使用安全随机数和原子消费。 |
| 高 | `ADMIN` 被当成超级管理员 | 超级管理员角色统一为 `ROOT`，重新计算历史令牌标志；防止普通管理员管理超管账号、修改或授予超管角色。 |
| 高 | 续期丢失部门、角色与数据范围 | 两种令牌模式保留完整认证上下文；缺少上下文的旧刷新令牌要求重新登录。 |
| 高 | Redis 登出后刷新令牌仍可使用 | 增加会话版本验证和原子消费；用户禁用、密码、角色及权限变更撤销旧会话。 |
| 高 | 无数据范围默认放行，详情和管理操作缺少范围检查 | 无有效范围拒绝返回数据，用户详情、编辑、删除等校验可管理范围。 |
| 高 | 部分管理接口允许匿名读取或删除配置 | 日志统计、字典、角色与代码生成接口补充认证；配置值读取及代码生成配置删除补充权限。 |
| 高 | 任意登录用户可删除其他人的存储文件 | 新上传路径包含用户 ID；删除校验存储地址、桶、路径及归属，旧文件由管理员管理。 |
| 中 | Web 刷新令牌放在查询参数中 | 改为后端要求的 JSON 请求体。 |
| 中 | 跨域来源配置被误用作正则，自定义平台请求头被拒绝 | 使用明确来源列表，允许客户端平台及版本请求头。 |
| 中 | 部门编辑丢失父级，路径包含自身，可形成循环 | 修复字段映射和祖先路径，拒绝自身、下级及不存在的父部门。 |
| 中 | 角色选项返回 `id/name`，客户端需要 `value/label` | 使用仅用于校验的别名，保持响应字段正确。 |
| 中 | 无效批量 ID 触发 500 | 部门、用户、角色和字典统一校验正整数、数量及重复 ID。 |
| 中 | 移动端新检出无法直接类型检查，组件插槽类型不兼容 | 纳入自动导入声明，调整编译器插槽推断，增加依赖锁文件和明确的依赖构建许可。 |
| 低 | 测试路径过期、错误码字符串转换及无用导入 | 更新真实接口路径，修正转换，清理 Python 静态错误。 |

### 验证结果

- 后端：116 项测试全部通过，整体语句覆盖率 61%；新增回归覆盖认证绕过、续期撤销、超管保护、字段映射、部门循环、批量参数和文件归属。
- Python `ruff check app tests --select F`：通过。
- Web：类型检查、生产构建、ESLint 和 Stylelint 均通过；ESLint 仍有 40 条现存警告，构建仍提示大文件包。
- 移动端：`pnpm check` 全部通过；H5 生产构建通过。
- 本地后端已重启以应用认证及配置修复。

### 使用变化与验证边界

1. 本地签名密钥已更换，现有会话需要重新登录。其它部署必须设置自己的 `JWT_SECRET_KEY`，不能直接使用空白示例配置。
2. 短信、邮件及微信验证尚未配置真实服务，对应接口返回 501；账号密码登录保留。恢复这些入口前应实现服务端身份验证、验证码过期与一次性消费。
3. 既有部门路径不会被批量改写；本次修复保证新建、移动和级联更新使用正确祖先路径。历史异常数据需单独核查。
4. 全量 Ruff 尚未通过，主要包含 FastAPI 参数默认值、API 驼峰命名及现存风格规则差异；未通过的检查未被隐藏或算作通过。
5. 未进行真实短信、微信、邮件及对象存储端到端操作，也未运行移动端真机测试。自动化测试不等于逐页交互验收，61% 覆盖率仍有测试空白。
