<template>
  <view>
    <view class="pt-20rpx">
      <wd-card v-if="userProfile">
        <wd-cell-group border>
          <wd-cell title="头像" center is-link>
            <view class="avatar-cell__avatar">
              <view v-if="!userProfile.avatar" class="avatar-cell__img" @click="handleAvatarUpload">
                <wd-icon name="camera-fill" custom-class="avatar-cell__img-icon" />
              </view>
              <image
                v-if="userProfile.avatar"
                class="avatar-cell__img"
                :src="userProfile.avatar"
                mode="aspectFit"
                @click="handleAvatarUpload"
              />
            </view>
          </wd-cell>
          <wd-cell title="昵称" :value="userProfile.nickname" is-link @click="openDialog()" />
          <wd-cell
            title="性别"
            :value="userProfile.gender === 1 ? '男' : userProfile.gender === 2 ? '女' : '未知'"
            is-link
            @click="openDialog()"
          />
          <wd-cell title="用户名" :value="userProfile.username" />
          <wd-cell title="部门" :value="userProfile.deptName" />
          <wd-cell title="角色" :value="userProfile.roleNames" />
          <view class="profile-last-cell-wrap">
            <wd-cell title="创建日期" :value="formatDateTime(userProfile.createTime)" />
          </view>
        </wd-cell-group>
      </wd-card>
    </view>

    <!--头像裁剪-->
    <wd-img-cropper
      v-if="avatarShow"
      v-model="avatarShow"
      :img-src="originalSrc"
      @confirm="handleAvatarConfirm"
    />

    <!--用户信息编辑弹出框-->
    <wd-popup v-if="dialogState.visible" v-model="dialogState.visible" position="bottom">
      <wd-form
        ref="userProfileFormRef"
        :model="userProfileForm"
        :schema="rules"
        title-width="160rpx"
        custom-class="pt-40rpx"
      >
        <wd-cell-group border>
          <wd-form-item prop="nickname" title="昵称" required>
            <wd-input v-model="userProfileForm.nickname" placeholder="请输入昵称" />
          </wd-form-item>
          <wd-form-item prop="gender" title="性别" required center>
            <wd-radio-group
              v-model="userProfileForm.gender"
              type="button"
              class="leading-none text-left"
            >
              <wd-radio :value="1">男</wd-radio>
              <wd-radio :value="2">女</wd-radio>
            </wd-radio-group>
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
import UserAPI, { type UserProfile, UserProfileForm } from "@/api/user";
import FileAPI, { type FileInfo } from "@/api/file";
import { checkLogin } from "@/utils/auth";
import { getErrorMessage } from "@/utils/error";
import { formatDateTime } from "@/utils/format";
import { toFormSchema } from "@/utils/form-schema";

definePage({
  name: "profile",
  style: { navigationBarTitleText: "我的资料" },
});

const toast = useToast();
const originalSrc = ref<string>(""); //选取的原图路径
const avatarShow = ref<boolean>(false); //显示头像裁剪
const userProfile = ref<UserProfile>(); //用户信息

/** 加载用户信息 */
const loadUserProfile = async () => {
  userProfile.value = await UserAPI.getProfile();
};

// 头像选择
function handleAvatarUpload() {
  uni.chooseImage({
    count: 1,
    success: (res) => {
      originalSrc.value = res.tempFilePaths[0];
      avatarShow.value = true;
    },
  });
}
// 头像裁剪完成
/** wd-img-cropper 裁剪确认事件 */
interface ImgCropperConfirmEvent {
  tempFilePath: string;
}

function handleAvatarConfirm(event: ImgCropperConfirmEvent) {
  const { tempFilePath } = event;
  FileAPI.upload(tempFilePath)
    .then((fileInfo: FileInfo) => {
      const avatarForm: UserProfileForm = {
        avatar: fileInfo.url,
      };
      // 头像路径保存至后端
      return UserAPI.updateProfile(avatarForm);
    })
    .then(() => {
      toast.info("头像上传成功");
      loadUserProfile();
    })
    .catch((error) => {
      toast.info(getErrorMessage(error, "头像上传失败"));
    });
}

// 本页面中所有的校验规则
const rules = toFormSchema({
  nickname: [{ required: true, message: "请填写昵称" }],
  gender: [{ required: true, message: "请选择性别" }],
});

const dialogState = reactive({
  visible: false,
});

const userProfileForm = reactive<UserProfileForm>({});
const userProfileFormRef = ref();

/**
 * 打开弹窗
 * @param type 弹窗类型 ACCOUNT: 账号资料 PASSWORD: 修改密码 MOBILE: 绑定手机 EMAIL: 绑定邮箱
 */
const openDialog = () => {
  dialogState.visible = true;
  // 初始化表单数据
  userProfileForm.nickname = userProfile.value?.nickname;
  userProfileForm.gender = userProfile.value?.gender;
};

// 提交表单
function handleSubmit() {
  userProfileFormRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (valid) {
      UserAPI.updateProfile(userProfileForm).then(() => {
        toast.info("账号资料修改成功");
        dialogState.visible = false;
        loadUserProfile();
      });
    }
  });
}

// 检查登录状态
onLoad(() => {
  if (!checkLogin()) return;

  // #ifdef H5
  document.addEventListener("touchstart", handleTouchStart, { passive: false });
  document.addEventListener("touchmove", handleTouchMove, { passive: false });
  // #endif
  loadUserProfile();
});

// 页面销毁前移除事件监听
onBeforeUnmount(() => {
  // #ifdef H5
  document.removeEventListener("touchstart", handleTouchStart);
  document.removeEventListener("touchmove", handleTouchMove);
  // #endif
});
// 禁用浏览器双指缩放，使头像裁剪时双指缩放能够起作用
function handleTouchStart(event: TouchEvent) {
  if (event.touches.length > 1) {
    event.preventDefault();
  }
}
// 禁用浏览器下拉刷新，使头像裁剪时能够移动图片
function handleTouchMove(event: TouchEvent) {
  event.preventDefault();
}
</script>
<style lang="scss" scoped>
// 头像行内容较高，需显式居中
:deep(.wd-cell__body) {
  align-items: center;
}

.avatar-cell__avatar {
  display: flex;
  align-items: center;
  // 小程序端不支持 justify-content: right
  justify-content: flex-end;
  width: 100%;
}

.avatar-cell__img {
  position: relative;
  width: 112rpx;
  height: 112rpx;
  background-color: var(--color-fill-1);
  border-radius: 50%;
}

.avatar-cell__img-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  color: var(--color-text-inverse);
  transform: translate(-50%, -50%);
}
</style>
