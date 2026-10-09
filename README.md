# Wubi86 × Qingjian English Gloss for Rime / 仓输入法

在 iPhone 上用 **仓输入法（Hamster）+ Rime 五笔86**，输入中文时在候选旁显示英文词汇释义。核心离线、无需付费 API。这个项目是**独立社区配置，不属于青简或仓输入法官方项目**。

> **状态：v0.1 实验配置。** 已有 iPhone 用户确认：启用仓输入法的「显示候选 Comment」后，五笔中文候选可以显示英文注释。不同仓版本、皮肤及长英文截断效果仍待进一步测试。

## 下载和安装（iPhone）

1. 在项目主页点 `Actions` → 最新绿色的 `Build Hamster Wubi86 + English Gloss` → 底部下载 `hamster-wubi86-qingjian` 构建产物。GitHub 会给你一个外层 zip；在 iPhone 的「文件」App **解压一次**，得到 `hamster-wubi86-qingjian.zip`。
2. 在 iPhone 安装「仓输入法 Hamster」，先在 App 内给原有输入方案做好备份。
3. 仓 → **输入方案设置** → 右上角 **+** → **导入方案** → 选择 `hamster-wubi86-qingjian.zip`；重新部署，选取「五笔86 · 英文释义」。仓要求导入的 ZIP 内**不能多套一层根文件夹**，构建脚本已经处理。
4. **必做：打开仓输入法 App →「键盘设置」→「候选栏设置」→ 开启「显示候选 Comment」。** 本项目把英文显示在候选注释（Comment）中，关闭该选项就会出现「五笔能打出汉字，但看不到英文」的情况；如字太小，可调整「候选字 Comment 字体大小」。
5. 在 iPhone「设置 → 通用 → 键盘 → 键盘」启用仓输入法。打开备忘录，试打「苹果、开发、编程」的五笔编码；在候选栏寻找 `apple / develop / programming` 等注释。
6. Rime 的 `英释开/英释关` 状态可以关闭注释；具体切换入口由仓前端提供。

**重要：这个完整包包含 `default.custom.yaml`，会覆盖你已有的同名配置，且替换原有 Rime 方案列表。** 已经在用 Rime 的用户请先备份仓的 Rime 文件夹；恢复旧方案请恢复原 `default.custom.yaml`，或手动合并 `schema_list`。新的五笔方案另命名为 `wubi86_qj`，不会覆写 `wubi86` 词库。

仓的导入说明：https://ihsiao.com/apps/hamster/docs/guides/input_schema/

### 常见问题：有中文候选但没有英文

1. 先检查仓输入法 App → **键盘设置 → 候选栏设置 →「显示候选 Comment」** 是否开启。**这是已在 iPhone 上验证有效的关键设置。**
2. 确认使用「五笔86 · 英文释义」方案，且 `英释开` 已启用。
3. 如果依旧没有英文，再尝试在仓的 RIME 设置中「重新部署」，回到备忘录重新输入测试。
4. 如果 `gg` 等编码连汉字候选也没有，请先确认当前是中文输入模式、且已经切换到正确方案。这与注释显示问题不同。

## v6 字母垂直居中修复（针对 v5）

已在 iPhone 实测发现：v5 键帽中的字母位置明显偏上（图像比较，第一排字母视觉上约高出目标 19px）。原因是我们自定义皮肤将文字前景的 `center.y` 设成了 `0.52`，而参考皮肤使用更靠下的位置。v6 仅将 26 键字母前景统一调整为 `center.y: 0.80`，将底排标点及 `123` 等文本前景调整为 `0.78`；**图形功能键、按键大小、动作绑定、键盘透明底色以及中文/英文词典均不改变**。

已有 v5 .hskin 文件时，可运行 `python3 scripts/recenter_skin.py native-clear-ios-v5.hskin native-clear-ios-v6.hskin` 生成修复版。该脚本基于 v5 的打包布局，不能直接套用于仓其他作者的皮肤；结果尚需在 iPhone 上验证。GitHub 现有的 `scripts/build_skin.py` 仍为早期生成器，待后续将 v5/v6 外观源代码完整合并入自动构建。

## 原生风格键盘皮肤（可选）
 
本项目另附一套独立的仓输入法 `.hskin` 皮肤「**原生·清晰 / Native Clear**」，风格参考 iPhone 系统键盘，但并非苹果官方皮肤。只包含原创配色与配置，不包含第三方商业字体或苹果图片素材。
 
- **v4 外观重做**：依据 iPhone 实测截图反馈，字母默认小写、字重 `medium`，键帽改为 8.5pt 圆角、缩短键盘高度，不再使用醒目的蓝色回车。
- **透明底板**：不在第三方皮肤中伪造苹果专有的毛玻璃效果，而是把区域背景设为极低透明度，尽可能保留 iOS 系统键盘底部已有的模糊背景；实际观感取决于仓版本及 iOS 系统。
- **布局**：顶部不再是孤零零的 `⌘`，改为常用标点快捷栏；底部为 `123`、表情、宽空格、回车。iOS 系统的地球键位于键盘最底部，无需在皮肤中重复。中英切换可通过输入方案菜单处理（`123` 下划）。
- **中英释义**：候选中文字 18pt，英文 Comment 11.5pt，输入方案和词库无需重装。
- **设备**：iPhone 竖屏／横屏、iPad 配置均已生成，仍需在不同设备上验证。
 
**安装（与词库分开，不需要再次部署 Rime）**：
 
1. 在 [GitHub Actions](https://github.com/No3456bite/rime-wubi-qingjian/actions) 打开最新成功的 `Build Hamster Wubi86 + English Gloss`，下载 `native-clear-ios-skin` 构建产物（GitHub 会下载外层 ZIP）。
2. 在 iPhone「文件」中**仅解压 GitHub 下载的外层 ZIP 一次**，取得里面的 `native-clear-ios.hskin`。**不要再解压 `.hskin` 本身！** 这是一个虽然内部采用 ZIP、但应当作为独立皮肤安装包共享的文件。
3. 在「文件」App 中长按 `native-clear-ios.hskin` →「共享」→「仓输入法」或「用仓打开」。**不要把 `.hskin` 当作输入方案 ZIP 导入 RIME，也不要把里面的 `dark/`、`light/` 文件夹分别导入键盘皮肤。**
4. 在仓的「键盘皮肤」中应该只出现一个名为「原生·清晰」的项目（而不是独立的「dark」「light」），选中并启用。
5. **继续保持「键盘设置 → 候选栏设置 → 显示候选 Comment」开启**，否则英文释义依然不可见。

**关于此前 v1/v2 的报错：** 旧版 `.hskin` 把 `config.yaml`、`dark/`、`light/` 直接放在压缩包根目录；仓把 `dark`、`light` 误当成独立皮肤，报找不到 `config.yaml`。这不是 Rime 字典的问题，也不需要重新部署 Rime。用户已证实社区「26键·万象」能正常导入；2026-10-09 检查其发布的原始 `.hskin` 后确认正确封装是**根目录唯一皮肤文件夹**。从 v3 开始严格参照此结构，v4 继续沿用已验证可导入的封装：

```text
native-clear-ios.hskin   ← 将 .hskin 文件整体交给仓导入，不要解压
└── native-clear-ios/    ← 关键：多这一层皮肤文件夹
    ├── config.yaml
    ├── light/
    │   └── qwerty_portrait.yaml
    └── dark/
        └── qwerty_portrait.yaml
```

**如果之前装过 v1/v2：** 在仓的「键盘皮肤」里删除报错的 `dark`、`light` 两项，再导入新包。安装后的排版还需 iPhone 真机验证；有异常先换回原皮肤。皮肤只影响显示，不会清空词库。

此皮肤不会更改 `wubi86_qj` 的输入词库，也不绑定别的拼音方案。首次版本通过静态配置检查，但尚未在实际 iPhone 上验证皮肤导入与具体显示效果；若布局偏移或功能键失效，请暂时切回原皮肤并反馈截图。
 
可在本地用 `python3 scripts/build_skin.py` 构建 `dist/native-clear-ios.hskin`，用 `--check` 检查布局引用。无需联网或额外 Python 依赖。
 
## 从源码重新构建

需要 Python 3.10+，建议系统安装 `opencc_dict` 用于编译 `.ocd2`，减少手机运行时首次加载词典的开销。首次构建联网从上游下载两个源文件与授权文本。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

生成 `dist/hamster-wubi86-qingjian.zip`。构建会自动下载青简英文译词表和 Rime 官方五笔86码表；无需专用账号、模型或收费服务。也可提供本地文件：

```bash
python3 scripts/build.py --glossary path/to/glossary-en.tsv --wubi-dict path/to/wubi86.dict.yaml --wubi-license path/to/RIME_LICENSE
```

已安装 `opencc_dict` 时编译二进制 OpenCC 字典；没有安装会退回文本字典，前端兼容性与性能更不确定。CI 在 Ubuntu 安装 OpenCC，正常情况下始终生成二进制版。

## 技术细节

- 五笔86词库：Rime 官方表，编译时命名空间改为 `wubi86_qj`，避免污染用户已有五笔方案。
- 英文词条：青简 `glossary-en.tsv`，第一条释义转换成 OpenCC 映射，按候选中文字查表，常见词约 23 万条，具体以构建日志为准。
- Rime：`simplifier@qingjian_en` 配合 `show_in_comment: true`，**英文是注释，不上屏**。默认 `英释开`，可以切换。
- `OpenCC` 的转换并非严格词典级查表：找不到精确词条时可能对词语局部匹配，产生不自然的注释。后续可研究 Lua Filter 或其他全词匹配办法；不在 v0.1 里冒险修改输入行为。
- OpenCC 文本字典会把英文释义内的普通空格理解为备选分隔符，因此构建把释义里的普通空格改为不换行空格（NBSP）。候选栏可能仍截断太长的释义。
- 无学习进度同步、无智能句子翻译、无第三方云查询。

## 安全和开源声明

运行时不需要联网，不含遥测、账号、输入上传、远程执行或私钥；构建时从公开的上游 GitHub 下载资源。输入法本身权限由你安装的仓 App 决定。请仅在你信任的输入法 App 中部署。

- **配置/转换脚本**：GPL-3.0-or-later（本仓库 `LICENSE`）。
- **青简英文释义**：qingjian-team/qingjian，GPL-3.0-or-later。词表在 CI 构建时下载，不将上游大文件直接加入源码仓库。
- **Rime 五笔86词典**：rime/rime-wubi，LGPL-3.0。打包时带上原许可文本与来源声明。
- **仓输入法**：imfuxiao/Hamster，仅作为运行容器，与本项目无隶属关系。

源码修改或分发时须保留相关版权与许可说明。参见 `THIRD_PARTY.md`。

## 待办

- [x] 在 iPhone 的仓输入法中验证五笔中文候选旁的英文注释（需开启「显示候选 Comment」；更多设备和皮肤仍待测试）。
- [ ] 候选栏长释义截断策略与词义过滤。
- [ ] 在保留现有 `default.custom.yaml` 的前提下安装（目前是干净安装模式）。
- [ ] 支持极点五笔86和自定义 Wubi 码表。
- [ ] 可切换只显示高频英语词汇的学习模式。
- [ ] 可选日语词库、英语熟悉度标记。