# vibocoding助手

面向 Vibe Coding 初学者的界面速查网站。包含 UI 元素、动效、布局与响应式、视觉风格、交互规则、页面类型、数据可视化及 UI 与交互 Skills 八类，共 152 个可查条目。前七类提供示例与实现需求，Skills 类提供 GitHub 来源和可复制的 Codex 安装提示词。

## 本地构建与预览

需要 Python 3。网站本身不依赖后端或第三方前端包。

```bash
python3 scripts/build_site.py
python3 -m http.server 4173 --directory dist
```

在浏览器打开 `http://localhost:4173/`。构建结果位于 `dist/`，可以交给静态网站托管服务。发布时以 `dist/` 为根目录，不要把整个工作区作为网站根目录。

## 内容维护

- UI 元素：编辑 `网页UI元素速查.html`。
- 动效：编辑 `动效速查-src/motion_entries.json` 和 `动效速查-src/motion_template.html`；新增演示分别在 `动效速查-src/extra_demos.py`、`动效速查-src/motion_extra.css`、`动效速查-src/motion_extra.js`。构建脚本会先重新生成 `动效速查.html`。
- 首页与共用导航：编辑 `site-src/index.html`、`site-src/site.css` 和 `site-src/site.js`。
- 其他五类速查：在 `site-src/guide_pages.py` 中维护内容和 HTML，在 `site-src/guides.css`、`site-src/guides.js` 中维护共用视觉和示例交互；视觉风格的六套风格样式在 `site-src/visual-styles.css`。
- UI 与交互 Skills：在 `site-src/skill_catalog.py` 中维护条目和安装提示词，在 `site-src/skills.css`、`site-src/skills.js` 中维护页面样式与交互。
- 站点输出：`scripts/build_site.py` 使用明确的文件清单构建首页、七类速查页、Skills 页、两个跨页转场演示页及共用资源；同目录中的其他文件不会进入 `dist/`。

运行构建检查：

```bash
python3 -m unittest discover -s tests -p 'test_site_build.py'
```

每个条目保留稳定的 HTML 锚点。例如 `/ui/#c-button`、`/motion/#e-view-crossfade` 和 `/layout/#g-layout-grid`。站点在卡片下方提供直达与复制链接操作。
