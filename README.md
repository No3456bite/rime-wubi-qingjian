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