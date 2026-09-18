/**
 * uni-app 原生组件类型声明
 *
 * 解决 Volar 对原生组件属性的类型检查问题
 * 这些类型声明扩展了 @uni-helper/uni-types 的基础类型
 */

// 扩展 uni-app 原生组件属性类型
declare module "@vue/runtime-core" {
  export interface GlobalComponents {
    view: import("vue").DefineComponent<{
      class?: string;
      style?: string | Record<string, any>;
      hoverClass?: string;
      hoverStartTime?: number;
      hoverStayTime?: number;
      hoverStopPropagation?: boolean;
      onClick?: (event: any) => void;
    }>;
    text: import("vue").DefineComponent<{
      class?: string;
      style?: string | Record<string, any>;
      selectable?: boolean;
      userSelect?: boolean;
      space?: "ensp" | "emsp" | "nbsp";
      decode?: boolean;
      onClick?: (event: any) => void;
    }>;
    image: import("vue").DefineComponent<{
      class?: string;
      style?: string | Record<string, any>;
      src?: string;
      mode?:
        | "scaleToFill"
        | "aspectFit"
        | "aspectFill"
        | "widthFix"
        | "heightFix"
        | "top"
        | "bottom"
        | "center"
        | "left"
        | "right"
        | "top left"
        | "top right"
        | "bottom left"
        | "bottom right";
      lazyLoad?: boolean;
      fadeShow?: boolean;
      webp?: boolean;
      showMenuByLongpress?: boolean;
      onClick?: (event: any) => void;
    }>;
    button: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
        size?: "default" | "mini";
        type?: "primary" | "default" | "warn";
        plain?: boolean;
        disabled?: boolean;
        loading?: boolean;
        formType?: "submit" | "reset";
        openType?:
          | "feedback"
          | "share"
          | "getUserInfo"
          | "contact"
          | "getPhoneNumber"
          | "launchApp"
          | "openSetting"
          | "getAuthorize"
          | "contactShare"
          | "livestream"
          | "getRealnameAuthInfo";
        hoverClass?: string;
        hoverStartTime?: number;
        hoverStayTime?: number;
        lang?: "en" | "zh_CN" | "zh_TW";
        sessionFrom?: string;
        sendMessageTitle?: string;
        sendMessagePath?: string;
        sendMessageImg?: string;
        showMessageCard?: boolean;
        appParameter?: string;
        onClick?: (event: any) => void;
        onGetphonenumber?: (event: any) => void;
        onGetuserinfo?: (event: any) => void;
        onContact?: (event: any) => void;
        onError?: (event: any) => void;
        onOpensetting?: (event: any) => void;
        onLaunchapp?: (event: any) => void;
      };
    };
    input: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
        value?: string;
        type?: "text" | "number" | "idcard" | "digit" | "safe-password" | "nickname";
        password?: boolean;
        placeholder?: string;
        placeholderStyle?: string;
        placeholderClass?: string;
        disabled?: boolean;
        maxlength?: number | string;
        cursorSpacing?: number;
        autoFocus?: boolean;
        focus?: boolean;
        cursor?: number;
        selectionStart?: number;
        selectionEnd?: number;
        adjustPosition?: boolean;
        holdKeyboard?: boolean;
        alwaysEmbed?: boolean;
        confirmType?: "send" | "search" | "next" | "go" | "done";
        confirmHold?: boolean;
        onInput?: (event: any) => void;
        onFocus?: (event: any) => void;
        onBlur?: (event: any) => void;
        onConfirm?: (event: any) => void;
      };
    };
    textarea: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
        value?: string;
        placeholder?: string;
        placeholderStyle?: string;
        placeholderClass?: string;
        disabled?: boolean;
        maxlength?: number | string;
        autoFocus?: boolean;
        focus?: boolean;
        autoHeight?: boolean;
        fixed?: boolean;
        cursorSpacing?: number;
        cursor?: number;
        showConfirmBar?: boolean;
        selectionStart?: number;
        selectionEnd?: number;
        adjustPosition?: boolean;
        holdKeyboard?: boolean;
        disableDefaultPadding?: boolean;
        confirmType?: "send" | "search" | "next" | "go" | "done";
        confirmHold?: boolean;
        onInput?: (event: any) => void;
        onFocus?: (event: any) => void;
        onBlur?: (event: any) => void;
        onConfirm?: (event: any) => void;
        onLinechange?: (event: any) => void;
      };
    };
    scrollview: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
        scrollX?: boolean;
        scrollY?: boolean;
        upperThreshold?: number;
        lowerThreshold?: number;
        scrollTop?: number | string;
        scrollLeft?: number | string;
        scrollIntoView?: string;
        scrollWithAnimation?: boolean;
        enableBackToTop?: boolean;
        enableFlex?: boolean;
        scrollAnchors?: boolean;
        refresherEnabled?: boolean;
        refresherThreshold?: number;
        refresherDefaultStyle?: "black" | "white" | "none";
        refresherBackground?: string;
        refresherTriggered?: boolean;
        enhanced?: boolean;
        bounces?: boolean;
        showScrollbar?: boolean;
        pagingEnabled?: boolean;
        fastDeceleration?: boolean;
        onScrolltoupper?: (event: any) => void;
        onScrolltolower?: (event: any) => void;
        onScroll?: (event: any) => void;
        onRefresherrefresh?: (event: any) => void;
        onRefresherrestore?: (event: any) => void;
        onRefresherabort?: (event: any) => void;
      };
    };
    swiper: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
        indicatorDots?: boolean;
        indicatorColor?: string;
        indicatorActiveColor?: string;
        autoplay?: boolean;
        current?: number;
        interval?: number;
        duration?: number;
        circular?: boolean;
        vertical?: boolean;
        previousMargin?: string;
        nextMargin?: string;
        displayMultipleItems?: number;
        skipHiddenItemLayout?: boolean;
        easingFunction?: "default" | "linear" | "easeInCubic" | "easeOutCubic" | "easeInOutCubic";
        onChange?: (event: any) => void;
        onTransition?: (event: any) => void;
        onAnimationfinish?: (event: any) => void;
      };
    };
    swiperitem: new () => {
      $props: {
        class?: string;
        style?: string | Record<string, any>;
      };
    };
  }
}

export {};
