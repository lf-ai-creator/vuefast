/**
 * 工作台菜单配置
 */

export interface WorkMenuItem {
  icon: string;
  title: string;
  url: string;
  perm: string;
}

export interface WorkMenuGroup {
  title: string;
  children: WorkMenuItem[];
}

export const workMenuGroups: WorkMenuGroup[] = [
  {
    title: "系统管理",
    children: [
      {
        icon: "/static/icons/user.svg",
        title: "用户管理",
        url: "/subPages/work/user/index",
        perm: "sys:user:list",
      },
      {
        icon: "/static/icons/role.svg",
        title: "角色管理",
        url: "/subPages/work/role/index",
        perm: "sys:role:list",
      },
      {
        icon: "/static/icons/company.svg",
        title: "部门管理",
        url: "/subPages/work/dept/index",
        perm: "sys:dept:list",
      },
      {
        icon: "/static/icons/settings.svg",
        title: "系统配置",
        url: "/subPages/work/config/index",
        perm: "sys:config:list",
      },
      {
        icon: "/static/icons/file.svg",
        title: "字典管理",
        url: "/subPages/work/dict/index",
        perm: "sys:dict:list",
      },
      {
        icon: "/static/icons/menu.svg",
        title: "菜单管理",
        url: "/subPages/work/menu/index",
        perm: "sys:menu:list",
      },
      {
        icon: "/static/icons/bell.svg",
        title: "通知公告",
        url: "/subPages/work/notice/index",
        perm: "sys:notice:list",
      },
      {
        icon: "/static/icons/log.svg",
        title: "系统日志",
        url: "/subPages/work/log/index",
        perm: "sys:log:list",
      },
    ],
  },
  {
    title: "项目链接",
    children: [
      {
        icon: "/static/icons/company.svg",
        title: "官网",
        url: "https://www.youlai.tech/",
        perm: "",
      },
      {
        icon: "/static/icons/file.svg",
        title: "文档",
        url: "https://youlai.blog.csdn.net/article/details/143222890",
        perm: "",
      },
      {
        icon: "/static/icons/api.svg",
        title: "接口",
        url: "https://youlai.apifox.cn/",
        perm: "",
      },
      {
        icon: "/static/icons/repo.svg",
        title: "仓库",
        url: "https://atomgit.com/youlai/youlai-app",
        perm: "",
      },
    ],
  },
];
