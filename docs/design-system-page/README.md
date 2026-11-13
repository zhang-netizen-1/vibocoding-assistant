# 原设计系统网页离线副本

原设计系统网页的离线副本，导出自 `46f923e`，与公开站点脱钩。规范文本继续维护在 [docs/design-system.md](../design-system.md)。

双击 `index.html` 打开，或在仓库根目录执行以下命令，再访问终端显示的地址。

```sh
python3 -m http.server --directory docs/design-system-page
```

仅改写 `index.html` 的路径。资源引用从 `../assets/` 改为 `assets/`，保留版本查询参数。其他站点页面链接、搜索结果根路径和搜索索引地址改为 `https://zhang-netizen-1.github.io/vibocoding-assistant/` 下的绝对地址。自身链接与锚点保持原样。14 个资源文件逐字节复制，完整路径改写清单及原构建 SHA-256 见[校验清单](../../tests/fixtures/design_system_page_hashes.json)。

`demo-runtime.js` 按模板属性加载四份按钮演示样式，已随目录保存。CSS 中的 SVG 为内嵌 data URL，字体使用系统字体。页面展示和按钮演示使用本地资源，搜索需联网，通过 HTTPS 获取公开站点索引，搜索结果跳转到公开站点。
