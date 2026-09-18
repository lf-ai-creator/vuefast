<template>
  <view>
    <wd-card>
      <wd-cell-group border>
        <wd-cell
          icon="safe"
          title="账户密码"
          value="修改"
          is-link
          @click="handleOpenDialog(DialogType.PASSWORD)"
        />
        <wd-cell
          icon="mobile"
          title="绑定手机"
          :value="userProfile?.mobile || '未绑定手机号'"
          is-link
          @click="handleOpenDialog(DialogType.MOBILE)"
        />
        <wd-cell
          icon="email"
          title="绑定邮箱"
          :value="userProfile?.email ? userProfile.email : '未绑定邮箱'"
          is-link
          @click="handleOpenDialog(DialogType.EMAIL)"
        />
        <!-- #ifdef MP-WEIXIN -->
        <wd-cell icon="message" title="微信" value="解绑" is-link @click="handleUnbindWechat" />
        <!-- #endif -->
      </wd-cell-group>
    </wd-card>

    <!--用户信息编辑弹出框-->
    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-style="border-top-left-radius: 24rpx; border-top-right-radius: 24rpx;"
    >
      <wd-form
        v-if="dialog.type === DialogType.PASSWORD"
        ref="passwordChangeFormRef"
        :model="passwordChangeForm"
        :schema="passwordRules"
        title-width="160rpx"
        custom-class="pt-40rpx"
      >
        <wd-cell-group border>
          <wd-form-item prop="oldPassword" title="原密码" required>
            <wd-input
              v-model="passwordChangeForm.oldPassword"
              show-password
              clearable
              placeholder="请输入原密码"
            />
          </wd-form-item>
          <wd-form-item prop="newPassword" title="新密码" required>
            <wd-input
              v-model="passwordChangeForm.newPassword"
              show-password
              clearable
              placeholder="请输入新密码"
            />
          </wd-form-item>
          <wd-form-item prop="confirmPassword" title="确认密码" required>
            <wd-input
              v-model="passwordChangeForm.confirmPassword"
              show-password
              clearable
              placeholder="请确认新密码"
            />
          </wd-form-item>
        </wd-cell-group>
        <view class="p-24rpx">
          <wd-button size="large" block @click="handleSubmit">提交</wd-button>
        </view>
      </wd-form>
      <wd-form
        v-if="dialog.type === DialogType.MOBILE"
        ref="mobileBindingFormRef"
        :model="mobileBindingForm"
        :schema="mobileRules"
        title-width="160rpx"
        custom-class="pt-40rpx"
      >
        <wd-cell-group border>
          <wd-form-item prop="mobile" title="手机号码" required>
            <wd-input v-model="mobileBindingForm.mobile" clearable placeholder="请输入手机号码" />
          </wd-form-item>
          <wd-form-item prop="code" title="验证码" required>
            <wd-input v-model="mobileBindingForm.code" clearable placeholder="请输入验证码">
              <template #suffix>
                <wd-button
                  type=""
                  plain
                  :disabled="mobileCountdown > 0"
                  @click="handleSendVerificationCode('MOBILE')"
                >
                  {{ mobileCountdown > 0 ? `${mobileCountdown}s后重新发送` : "发送验证码" }}
                </wd-button>
              </template>
            </wd-input>
          </wd-form-item>
        </wd-cell-group>
        <view class="p-24rpx">
          <wd-button size="large" block @click="handleSubmit">提交</wd-button>
        </view>
      </wd-form>
      <wd-form
        v-if="dialog.type === DialogType.EMAIL"
        ref="emailBindingFormRef"
        :model="emailBindingForm"
        :schema="emailRules"
        title-width="160rpx"
        custom-class="pt-40rpx"
      >
        <wd-cell-group border>
          <wd-form-item prop="email" title="邮箱" required>
            <wd-input v-model="emailBindingForm.email" clearable placeholder="请输入邮箱" />
          </wd-form-item>
          <wd-form-item prop="code" title="验证码" required>
            <wd-input v-model="emailBindingForm.code" clearable placeholder="请输入验证码">
              <template #suffix>
                <wd-button
                  type=""
                  plain
                  :disabled="emailCountdown > 0"
                  @click="handleSendVerificationCode('EMAIL')"
                >
                  {{ emailCountdown > 0 ? `${emailCountdown}s后重新发送` : "发送验证码" }}
                </wd-button>
              </template>
            </wd-input>
          </wd-form-item>
        </wd-cell-group>
        <view class="p-24rpx">
          <wd-button size="large" block @click="handleSubmit">提交</wd-button>
        </view>
      </wd-form>
    </wd-popup>
  </view>
</template>
<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useToast, useDialog } from "@wot-ui/ui";
import { useCountdown } from "@/composables/useCountdown";
import { getErrorMessage } from "@/utils/error";
import { toFormSchema } from "@/utils/form-schema";
import UserAPI, {
  PasswordChangeForm,
  MobileBindingForm,
  EmailBindingForm,
  UserProfile,
} from "@/api/user";

definePage({
  name: "account",
  style: { navigationBarTitleText: "账号安全" },
});

const toast = useToast();
const { confirm } = useDialog();

// 本页面中所有的校验规则（三个弹窗表单分别绑定）
const passwordRules = toFormSchema({
  oldPassword: [{ required: true, message: "请填写原密码" }],
  newPassword: [{ required: true, message: "请填写新密码" }],
  confirmPassword: [
    {
      required: true,
      message: "请确认密码",
      validator: (value, model) => value === model.newPassword || "两次输入的密码不一致",
    },
  ],
});

const mobileRules = toFormSchema({
  mobile: [{ required: true, pattern: /^1[3-9]\d{9}$/, message: "请填写正确的手机号码" }],
  code: [{ required: true, message: "请填写验证码" }],
});

const emailRules = toFormSchema({
  email: [
    {
      required: true,
      pattern: /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/,
      message: "请填写正确的邮箱地址",
    },
  ],
  code: [{ required: true, message: "请填写验证码" }],
});

enum DialogType {
  PASSWORD = "password",
  MOBILE = "mobile",
  EMAIL = "email",
}

const dialog = reactive({
  visible: false,
  type: "" as DialogType, // 修改账号资料,修改密码、绑定手机、绑定邮箱
});

const userProfile = ref<UserProfile>(); //用户信息
const passwordChangeForm = reactive<PasswordChangeForm>({});
const mobileBindingForm = reactive<MobileBindingForm>({});
const emailBindingForm = reactive<EmailBindingForm>({});
const passwordChangeFormRef = ref();
const mobileBindingFormRef = ref();
const emailBindingFormRef = ref();

const { countdown: mobileCountdown, start: startMobileCountdown } = useCountdown(60);
const { countdown: emailCountdown, start: startEmailCountdown } = useCountdown(60);

const handleUnbindWechat = async () => {
  try {
    await confirm({
      title: "提示",
      msg: "确定要解绑微信吗？解绑后将无法使用微信小程序登录",
      headerImage: "warning",
    });
    await UserAPI.unbindSocial("WECHAT_MINI");
    toast.success("解绑成功");
    loadUserProfile();
  } catch {
    // 用户取消或解绑失败
  }
};

/** 加载用户信息 */
const loadUserProfile = async () => {
  userProfile.value = await UserAPI.getProfile();
};

/**
 * 打开弹窗
 * @param type 弹窗类型 ACCOUNT: 账号资料 PASSWORD: 修改密码 MOBILE: 绑定手机 EMAIL: 绑定邮箱
 */
const handleOpenDialog = (type: DialogType) => {
  dialog.type = type;
  dialog.visible = true;
  switch (type) {
    case DialogType.PASSWORD:
      passwordChangeForm.oldPassword = "";
      passwordChangeForm.newPassword = "";
      passwordChangeForm.confirmPassword = "";
      break;
    case DialogType.MOBILE:
      mobileBindingForm.mobile = "";
      mobileBindingForm.code = "";
      break;
    case DialogType.EMAIL:
      emailBindingForm.email = "";
      emailBindingForm.code = "";
      break;
  }
};

/**
 *  发送验证码
 *
 * @param contactType 联系方式类型 MOBILE: 手机号码  EMAIL: 邮箱
 */
const handleSendVerificationCode = async (contactType: string) => {
  try {
    if (contactType === "MOBILE") {
      const { valid } = await mobileBindingFormRef.value.validate("mobile");
      if (valid) {
        await UserAPI.sendVerificationCode(mobileBindingForm.mobile!, "MOBILE");
        toast.info("验证码已发送");
        startMobileCountdown();
      }
    } else if (contactType === "EMAIL") {
      const { valid } = await emailBindingFormRef.value.validate("email");
      if (valid) {
        await UserAPI.sendVerificationCode(emailBindingForm.email!, "EMAIL");
        toast.info("验证码已发送");
        startEmailCountdown();
      }
    }
  } catch (error) {
    toast.error(getErrorMessage(error, "验证码发送失败"));
  }
};

// 提交表单
async function handleSubmit() {
  try {
    if (dialog.type === DialogType.PASSWORD) {
      const { valid } = await passwordChangeFormRef.value.validate();
      if (valid) {
        await UserAPI.changePassword(passwordChangeForm);
        toast.info("密码修改成功");
        dialog.visible = false;
      }
    } else if (dialog.type === DialogType.MOBILE) {
      const { valid } = await mobileBindingFormRef.value.validate();
      if (valid) {
        await UserAPI.bindMobile(mobileBindingForm);
        toast.info("手机号绑定成功");
        dialog.visible = false;
        loadUserProfile();
      }
    } else if (dialog.type === DialogType.EMAIL) {
      const { valid } = await emailBindingFormRef.value.validate();
      if (valid) {
        await UserAPI.bindEmail(emailBindingForm);
        toast.info("邮箱绑定成功");
        dialog.visible = false;
        loadUserProfile();
      }
    }
  } catch (error) {
    toast.error(getErrorMessage(error, "提交失败"));
  }
}

onMounted(() => {
  loadUserProfile();
});
</script>
