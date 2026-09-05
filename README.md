# 西北风喝吗 · 个人主页

一个正式、简洁的静态个人网站，包含「关于我」「我的项目」「联系我」等板块，适配手机与电脑。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `index.html` | 网站主页（单文件，样式已内联） |
| `avatar.jpg` | 头像图片 |
| `favicon.png` | 浏览器标签页小图标 |

## 部署到 Cloudflare Pages（免费，自动分配 `xxx.pages.dev` 域名）

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)（没有账号先注册，免费）。
2. 左侧点 **Workers 和 Pages → 创建 → Pages → 连接到 Git**。
3. 授权并选择 GitHub 账号 **xbfhm**，选择本仓库（如 `homepage`），点击 **开始设置**。
4. 构建命令留空、输出目录留空（纯静态站，无需构建），点 **保存并部署**。
5. 部署完成后，网站地址形如 `https://xxx.pages.dev`，这就是你的免费域名。

> 也可以不用 GitHub：在 Pages 创建时选择 **直接上传（Direct Upload）**，把 `index.html`、`avatar.jpg`、`favicon.png` 三个文件一起拖进去上传即可。

## 修改内容

- 头像：替换根目录下的 `avatar.jpg`（建议正方形，512×512 左右）。
- 文字、项目、链接：直接编辑 `index.html`，搜索对应文字修改即可。
