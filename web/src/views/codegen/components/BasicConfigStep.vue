<template>
  <div class="basic-config-step">
    <div class="basic-config-layout">
      <div class="basic-form-panel">
        <!-- 表信息卡片 -->
        <div class="config-card">
          <div class="card-header">
            <div class="header-icon icon-table">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="header-title">
              <div class="title">表信息</div>
              <div class="subtitle">数据库表名与业务映射</div>
            </div>
          </div>
          <el-form :model="formData" :rules="rules" :label-width="100" class="card-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="表名" prop="tableName">
                  <el-input v-model="formData.tableName" readonly>
                    <template #prefix>
                      <el-icon><Document /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="业务名" prop="businessName">
                  <el-input v-model="formData.businessName" placeholder="如：用户管理">
                    <template #prefix>
                      <el-icon><OfficeBuilding /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 生成配置卡片 -->
        <div class="config-card">
          <div class="card-header">
            <div class="header-icon icon-gen">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="header-title">
              <div class="title">生成配置</div>
              <div class="subtitle">代码生成规则与输出选项</div>
            </div>
          </div>
          <el-form
            ref="formRef"
            :model="formData"
            :rules="rules"
            :label-width="100"
            class="card-form"
          >
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="业务模块" prop="moduleName">
                  <el-input v-model="formData.moduleName" placeholder="如：system">
                    <template #prefix>
                      <el-icon><Collection /></el-icon>
                    </template>
                  </el-input>
                  <div class="field-tip">决定 server/app、web/src 与 app/src 下的业务目录</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="实体名" prop="entityName">
                  <el-input v-model="formData.entityName" placeholder="User">
                    <template #prefix>
                      <el-icon><Coin /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="作者">
                  <el-input v-model="formData.author" placeholder="youlai">
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="移除表前缀">
                  <el-input v-model="formData.removeTablePrefix" placeholder="如: sys_">
                    <template #prefix>
                      <el-icon><Delete /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="页面类型">
                  <el-radio-group v-model="formData.pageType" size="large">
                    <el-radio-button value="classic">
                      <el-icon><DocumentChecked /></el-icon>
                      普通
                    </el-radio-button>
                    <el-radio-button value="curd">
                      <el-icon><SetUp /></el-icon>
                      封装(CURD)
                    </el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item>
                  <template #label>
                    <div class="flex items-center gap-2">
                      <span>上级菜单</span>
                      <el-tooltip effect="dark" placement="top">
                        <template #content>
                          <div style="max-width: 280px; line-height: 1.8">
                            选择上级菜单，生成代码后会自动创建对应菜单。
                            <br />
                            注意：生成菜单后需分配权限给角色，否则菜单将无法显示。
                          </div>
                        </template>
                        <el-icon class="cursor-pointer text-gray-400 hover:text-primary">
                          <QuestionFilled />
                        </el-icon>
                      </el-tooltip>
                    </div>
                  </template>
                  <el-tree-select
                    v-model="formData.parentMenuId"
                    placeholder="选择上级菜单"
                    :data="menuOptions"
                    check-strictly
                    :render-after-expand="false"
                    filterable
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 实时生成结果 -->
      </div>

      <aside class="config-card output-preview-card">
        <div class="card-header">
          <div class="header-icon icon-output">
            <el-icon><Files /></el-icon>
          </div>
          <div class="header-title">
            <div class="title">生成文件预览</div>
            <div class="subtitle">文件路径与注释会随基础配置实时更新</div>
          </div>
          <el-tag type="success" effect="plain">{{ generatedFileCount }} 个文件</el-tag>
        </div>

        <div class="output-summary">
          <div>
            <span>数据表</span>
            <strong>{{ formData.tableName || "-" }}</strong>
          </div>
          <div>
            <span>业务名称</span>
            <strong>{{ formData.businessName || "-" }}</strong>
          </div>
          <div>
            <span>代码实体</span>
            <strong>{{ formData.entityName || "-" }}</strong>
          </div>
          <div>
            <span>页面模式</span>
            <strong>{{ formData.pageType === "curd" ? "CURD 封装" : "标准页面" }}</strong>
          </div>
        </div>

        <el-tabs v-model="activeOutputScope" class="output-tabs">
          <el-tab-pane v-for="group in generatedFileGroups" :key="group.scope" :name="group.scope">
            <template #label>
              <span class="output-tab-label">
                <el-icon><component :is="group.icon" /></el-icon>
                {{ group.label }}
                <el-badge :value="group.files.length" type="primary" />
              </span>
            </template>

            <div class="file-list">
              <div v-for="file in group.files" :key="file.path" class="file-row">
                <div class="file-main">
                  <div class="file-title">
                    <el-icon><Document /></el-icon>
                    <code>{{ file.path }}</code>
                  </div>
                  <p>{{ file.description }}</p>
                </div>
                <div class="file-comment">
                  <span>文件注释</span>
                  <code>{{ file.comment }}</code>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenConfigForm } from "@/api/codegen";
import type { OptionItem } from "@/api/common";

const formData = defineModel<GenConfigForm>({ required: true });

defineProps<{
  menuOptions: OptionItem[];
}>();

const formRef = ref();
const activeOutputScope = ref("server");

interface GeneratedFileItem {
  path: string;
  description: string;
  comment: string;
}

interface GeneratedFileGroup {
  scope: "server" | "web" | "app";
  label: string;
  icon: string;
  files: GeneratedFileItem[];
}

const generatedFileGroups = computed<GeneratedFileGroup[]>(() => {
  const moduleName = formData.value.moduleName?.trim() || "module";
  const entityName = formData.value.entityName?.trim() || "Entity";
  const entityLower = entityName.charAt(0).toLowerCase() + entityName.slice(1);
  const entityPath = entityName.toLowerCase();
  const businessName = formData.value.businessName?.trim() || entityName;
  const author = formData.value.author?.trim() || "youlai-fastapi";
  const serverRoot = `server/app/${moduleName}/${entityLower}`;
  const webApiRoot = `web/src/api/${moduleName}/${entityPath}`;
  const webViewRoot = `web/src/views/${moduleName}/${entityPath}`;
  const appViewRoot = `app/src/subPages/work/${entityPath}`;
  const pyComment = (name: string) => `"""${businessName}${name} — 由 ${author} 生成。"""`;
  const tsComment = (name: string) => `/** ${businessName}${name} — 由 ${author} 生成。 */`;

  return [
    {
      scope: "server",
      label: "Server",
      icon: "Cpu",
      files: [
        {
          path: `${serverRoot}/__init__.py`,
          description: "模块导出与路由注册入口",
          comment: pyComment("模块"),
        },
        {
          path: `${serverRoot}/models.py`,
          description: "SQLAlchemy 数据模型",
          comment: pyComment("数据模型"),
        },
        {
          path: `${serverRoot}/schemas.py`,
          description: "Pydantic 查询、表单与响应模型",
          comment: pyComment("数据模型定义"),
        },
        {
          path: `${serverRoot}/service.py`,
          description: "分页查询与增删改业务服务",
          comment: pyComment("业务服务"),
        },
        {
          path: `${serverRoot}/router.py`,
          description: "FastAPI 路由与权限校验",
          comment: pyComment("接口路由"),
        },
      ],
    },
    {
      scope: "web",
      label: "Web",
      icon: "Monitor",
      files: [
        {
          path: `${webApiRoot}/index.ts`,
          description: "后台管理 API 请求封装",
          comment: tsComment("接口"),
        },
        {
          path: `${webApiRoot}/types.ts`,
          description: "查询参数、表单与列表类型",
          comment: tsComment("类型定义"),
        },
        {
          path: `${webViewRoot}/index.vue`,
          description: "Element Plus 管理页面",
          comment: tsComment("管理页面"),
        },
      ],
    },
    {
      scope: "app",
      label: "App",
      icon: "Iphone",
      files: [
        {
          path: `app/src/api/${entityPath}.ts`,
          description: "uni-app API 请求封装",
          comment: tsComment("移动端接口"),
        },
        {
          path: `${appViewRoot}/index.vue`,
          description: "uni-app 移动端业务页面",
          comment: tsComment("移动端页面"),
        },
      ],
    },
  ];
});

const generatedFileCount = computed(() =>
  generatedFileGroups.value.reduce((total, group) => total + group.files.length, 0)
);

const rules = {
  tableName: [{ required: true, message: "请输入表名", trigger: "blur" }],
  businessName: [{ required: true, message: "请输入业务名", trigger: "blur" }],
  moduleName: [{ required: true, message: "请输入模块名", trigger: "blur" }],
  entityName: [{ required: true, message: "请输入实体名", trigger: "blur" }],
};

async function validate(): Promise<boolean> {
  try {
    await formRef.value?.validate();
    return true;
  } catch {
    return false;
  }
}

defineExpose({ validate });
</script>

<style scoped lang="scss">
.basic-config-step {
  padding: 8px;

  .config-card {
    padding: 24px;
    margin-bottom: 20px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--el-border-color);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    }

    .card-header {
      display: flex;
      gap: 14px;
      align-items: center;
      padding-bottom: 16px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--el-border-color-lighter);

      .header-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        font-size: 20px;
        border-radius: 10px;
        transition: transform 0.3s ease;

        &.icon-table {
          color: var(--el-color-primary);
          background: linear-gradient(
            135deg,
            var(--el-color-primary-light-8),
            var(--el-color-primary-light-9)
          );
        }
        &.icon-package {
          color: var(--el-color-success);
          background: linear-gradient(
            135deg,
            var(--el-color-success-light-8),
            var(--el-color-success-light-9)
          );
        }
        &.icon-gen {
          color: var(--el-color-warning);
          background: linear-gradient(
            135deg,
            var(--el-color-warning-light-8),
            var(--el-color-warning-light-9)
          );
        }
        &.icon-output {
          color: var(--el-color-primary);
          background: linear-gradient(
            135deg,
            var(--el-color-primary-light-8),
            var(--el-color-success-light-9)
          );
        }
      }

      &:hover .header-icon {
        transform: scale(1.08) rotate(-3deg);
      }

      .header-title {
        .title {
          margin-bottom: 4px;
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
        .subtitle {
          font-size: 13px;
          color: var(--el-text-color-secondary);
        }
      }
    }

    .card-form {
      .field-tip {
        width: 100%;
        margin-top: 4px;
        font-size: 12px;
        line-height: 1.35;
        color: var(--el-text-color-secondary);
      }

      :deep(.el-input__prefix-inner) {
        color: var(--el-text-color-secondary);
      }

      :deep(.el-radio-button__inner) {
        display: inline-flex;
        gap: 4px;
        align-items: center;
        padding: 10px 20px;
      }
    }
  }

  .output-preview-card {
    .card-header {
      .el-tag {
        margin-left: auto;
      }
    }
  }

  .output-summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 12px;

    > div {
      display: grid;
      gap: 5px;
      padding: 12px 14px;
      background: var(--el-fill-color-light);
      border-radius: 8px;
    }

    span {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    strong {
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 14px;
      white-space: nowrap;
    }
  }

  .output-tab-label {
    display: inline-flex;
    gap: 7px;
    align-items: center;

    :deep(.el-badge__content) {
      position: static;
      transform: none;
    }
  }

  .file-list {
    display: grid;
    gap: 10px;
  }

  .file-row {
    display: grid;
    grid-template-columns: minmax(280px, 1fr) minmax(280px, 0.9fr);
    gap: 18px;
    padding: 13px 16px;
    background: var(--el-fill-color-extra-light);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;

    .file-main {
      min-width: 0;
    }

    .file-title {
      display: flex;
      gap: 8px;
      align-items: center;
      min-width: 0;
      color: var(--el-color-primary);

      code {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    p {
      margin: 6px 0 0 24px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    .file-comment {
      display: grid;
      gap: 5px;
      min-width: 0;

      span {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }

      code {
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--el-text-color-regular);
        white-space: nowrap;
      }
    }
  }

  .basic-config-layout {
    display: grid;
    grid-template-columns: minmax(460px, 0.88fr) minmax(560px, 1.12fr);
    gap: 16px;
    align-items: start;
  }

  .basic-form-panel {
    display: grid;
    gap: 12px;

    .config-card {
      padding: 16px 18px;
      margin: 0;
      border-radius: 10px;
      box-shadow: none;

      &:hover {
        border-color: var(--el-border-color-lighter);
        box-shadow: none;
      }

      .card-header {
        gap: 10px;
        padding-bottom: 10px;
        margin-bottom: 12px;

        .header-icon {
          width: 32px;
          height: 32px;
          font-size: 16px;
          border-radius: 8px;
        }

        .header-title {
          .title {
            margin-bottom: 1px;
            font-size: 14px;
          }

          .subtitle {
            font-size: 12px;
          }
        }
      }

      .card-form {
        :deep(.el-form-item) {
          margin-bottom: 0;
        }

        :deep(.el-row + .el-row) {
          margin-top: 12px;
        }

        :deep(.el-radio-button__inner) {
          padding: 8px 13px;
        }
      }
    }
  }

  .output-preview-card {
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 205px);
    padding: 16px 18px;
    margin: 0;
    overflow: hidden;
    border-radius: 10px;
    box-shadow: none;

    &:hover {
      border-color: var(--el-border-color-lighter);
      box-shadow: none;
    }

    .card-header {
      flex: 0 0 auto;
      gap: 10px;
      padding-bottom: 10px;
      margin-bottom: 12px;

      .header-icon {
        width: 32px;
        height: 32px;
        font-size: 16px;
        border-radius: 8px;
      }

      .header-title {
        min-width: 0;

        .title {
          margin-bottom: 1px;
          font-size: 14px;
        }

        .subtitle {
          overflow: hidden;
          text-overflow: ellipsis;
          font-size: 12px;
          white-space: nowrap;
        }
      }
    }

    .output-summary {
      flex: 0 0 auto;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 6px;

      > div {
        gap: 3px;
        padding: 8px 10px;
      }
    }

    .output-tabs {
      display: flex;
      flex: 1;
      flex-direction: column;
      min-height: 0;

      :deep(.el-tabs__content) {
        flex: 1;
        min-height: 0;
        overflow: auto;
      }
    }

    .file-list {
      gap: 8px;
      padding-right: 2px;
    }

    .file-row {
      grid-template-columns: minmax(0, 1fr) minmax(185px, 0.82fr);
      gap: 10px;
      padding: 9px 10px;

      p {
        margin-top: 4px;
      }
    }
  }
}

@media (max-width: 1180px) {
  .basic-config-step {
    .basic-config-layout {
      grid-template-columns: 1fr;
    }

    .output-preview-card {
      position: static;
      max-height: none;

      .output-tabs {
        min-height: 300px;
      }
    }
  }
}

@media (max-width: 768px) {
  .basic-config-step {
    padding: 0;

    .config-card {
      padding: 16px;
      margin-bottom: 12px;
      border-radius: 8px;

      .card-header {
        gap: 10px;
        padding-bottom: 12px;
        margin-bottom: 12px;

        .header-icon {
          width: 36px;
          height: 36px;
        }
      }
    }

    .output-summary {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .file-row {
      grid-template-columns: 1fr;
      gap: 10px;
    }
  }
}
</style>
