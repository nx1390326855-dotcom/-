# 蓝蓝门店 · 生鲜商城首页

根据用户提供的首页参考图重建，画板 **426 × 924**；对应 **852 × 1848** 的两倍预览。保留原图的鲜绿色头部、搜索、轮播、十宫格分类、双促销卡、当季推荐、热销商品和五项底部导航。

- **[蓝蓝门店-首页.sketch](蓝蓝门店-首页.sketch)**：可编辑 Sketch 原生文件。
- **[蓝蓝门店-首页.svg](蓝蓝门店-首页.svg)**：独立 SVG，文字、形状和图标可编辑，商品摄影为内嵌 PNG，无外部图片依赖。
- [蓝蓝门店-首页.png](蓝蓝门店-首页.png)：从实际 Sketch 图层回读重建的高清检查预览。
- [设计稿预览.html](设计稿预览.html)：离线资源内嵌的检查预览。
- [验证结果.json](验证结果.json)：当前交付文件的校验结果。
- [素材](素材/)：16 张独立摄影素材，已嵌入 Sketch，打开文件无需联网。

![首页预览](蓝蓝门店-首页.png)

## 如何编辑

在 macOS Sketch 中打开 `.sketch`，按左侧图层列表展开模块。所有图层均未锁定：门店名、文案、分类、商品名、价格和数量为原生 Text；卡片、按钮、图标、轮播指示器和骑手为原生 Rectangle / Oval / ShapePath。共有 60 个文字图层、148 个形状图层、20 个摄影图层及 29 个分组；没有整页截图图层。

图片在各自的圆角蒙版分组内，选中“可替换摄影素材”即可替换。更改商品摄影时保留蒙版，避免影响相邻卡片。文字已配置共享样式，修改字号、粗细、颜色与对齐均可直接进行。

字体使用 **Noto Sans CJK SC Regular / Bold**（[Google 官方字体仓库](https://github.com/notofonts/noto-cjk)）。Mac 若提示缺失字体，请先安装字体，或在 Sketch 中统一替换为思源黑体/苹方并检查排版。

SVG 可在浏览器中查看，或导入支持 SVG 的矢量编辑器；采用标准 `<text>`、形状、路径、渐变和裁切，无 `foreignObject`。文字保留为文字，需要安装上述字体以获得一致排版；商品照片仍为位图。

摄影为按参考风格生成的替换素材，照片细节并非原图像素级复刻；骑手为独立原生矢量重绘。页面为静态设计稿，交互按钮没有连接业务后端。

## 重新生成与校验

在仓库根目录执行：

```bash
python3 'sketch/蓝蓝门店-首页/生成设计稿.py'
python3 'sketch/蓝蓝门店-首页/导出检查预览.py'
XDG_CACHE_HOME=/tmp/sketch-cache node 'sketch/蓝蓝门店-首页/渲染预览.js'
python3 'sketch/蓝蓝门店-首页/验证设计稿.py' --schema-dir /path/to/@sketch-hq/sketch-file-format/dist
```

Python 依赖 Pillow 和 jsonschema；Node 预览依赖 Playwright 和系统 Chromium。当前云环境已提供这些依赖。官方格式 Schema 可通过 `npm install --prefix /tmp/sketch-tools --ignore-scripts @sketch-hq/sketch-file-format@6.5.0` 获取，验证时传入 `/tmp/sketch-tools/node_modules/@sketch-hq/sketch-file-format/dist`。生成器复用同仓库 `sketch/会员中心/会员中心.sketch` 的格式模板，不更改该文件；摄影素材取自本目录 `素材/`。运行生成器会覆盖本目录生成的 Sketch 文件，编辑设计后请先保留自己的副本。

当前文件通过 `@sketch-hq/sketch-file-format@6.5.0` 官方 JSON Schema、ZIP 完整性、画板尺寸、共享文字样式引用、图片引用和文字宽度检查。PNG 从交付 `.sketch` 的真实图层重新读取并由 Chromium 绘制；**不是 Sketch 原生导出，尚未在 macOS Sketch 实机打开、渲染或保存验证**。
