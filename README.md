# 双栏批注论文 · bilingual-annotated-paper

把一篇学术论文变成一个**单文件、可离线打开的双栏批注 HTML**：左栏读文本，右栏读论证。

面向论文精读、课程阅读、论证结构拆解。批注不是读后感，而是论证工程图——每段回答三件事：这段在干什么活、它在论证链的哪一环、这一环最容易从哪里断。

## 成品长什么样

- **左栏**：英文原文（Lora 衬线）→ 五色高亮 → 1px 分隔线 → 中文意译（浅米色 `#f0ece2` 块 + 左侧竖线）
- **右栏**：逐段批注卡（左色边 + 浅背景）：段落功能 / 逻辑角色 / 论证技巧与潜在漏洞
- **底部**：论证骨架链（问题→论点→证据→反驳→结论）、一句话核心主张、最强处 vs 最弱处
- **顶部**：深海军蓝导航栏（标题 + 课程信息 + 五色图例）、sticky 章节导航（可跳转、当前节高亮）
- **响应式**：≤900px 自动单栏；打印友好；一键关闭高亮进入「纯净阅读」

## 五色约定

| 颜色 | 维度 | 标什么 |
|---|---|---|
| 黄 | 核心论点 thesis | 可被反驳、承担全文重量的 claim |
| 红 | 关键概念 / 术语 | 作者定义或改定义的术语 |
| 蓝 | 实证证据 / 数据 | 数据、样本、统计结果、案例、法条判例 |
| 绿 | 让步 / 反驳处理 | 自树对立面、条件限定、预先回应的异议 |
| 紫 | 方法论说明 | 抽样、识别策略、编码方式、比较单位 |

## 安装

把整个文件夹放进 agent 的 user skills 目录：

```bash
git clone https://github.com/Carlson620/bilingual-annotated-paper.git \
  ~/.doubao/agent_mode/workspace/.user_skills/bilingual-annotated-paper
```

（路径按你的运行环境调整；只要是 `.../workspace/.user_skills/<skill-name>` 即可。）

## 使用

技能被触发后，按 `SKILL.md` 的流程走；也可以直接调脚本：

```bash
# 1) 写内容 JSON（契约见 SKILL.md）
# 2) 渲染
python3 scripts/build.py content.json 论文-批注.html
# 分片构建（长篇论文按节写作）
python3 scripts/build.py content.json out.html --part part2.json --part part3.json
# 3) 结构自检（锚点、双栏配平、五色图例、断点、字体）
python3 scripts/check_output.py 论文-批注.html
```

## 目录

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 触发条件、六步工作流、内容 JSON 契约、视觉规范、质量红线 |
| `references/annotation-rubric.md` | 五维判定标准、段落功能词表、逻辑角色句式、意译规则、塌方自查表 |
| `assets/template.html` | 版式与样式唯一来源（含 sticky 导航、响应式、打印样式） |
| `scripts/build.py` | JSON → HTML 渲染，字段校验、危险标签剥离、按功能配批注卡色边 |
| `scripts/check_output.py` | 交付前结构自检，FAIL 即不可交付 |

## 依赖

- Python 3.8+，**仅标准库**，无需 pip 安装。
- 字体走 `miaoda.feishu.cn` 镜像（Lora / IBM Plex Sans / Noto Serif SC），断网时回落到系统字体，版面仍成立。

## 设计约束

- 英文原文一字不改，只允许在其外层加 `<mark>`；数字、引用、法条编号零改动。
- 中文译文以意译为主，不加高亮、不加批注，读起来像中文期刊论文。
- 高亮克制：每 100 词 1–2 处，单段不超过 6 处。
