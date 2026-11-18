---
name: bilingual-annotated-paper
display_name: "双栏批注论文"
description: 把一篇学术论文做成单文件「双栏批注 HTML」：左栏英文原文（五色高亮）＋紧接其下的中文意译，右栏逐段中文批注（段落功能、逻辑角色、论证技巧与漏洞），底部给出论证结构总览（骨架链、一句话主张、最强处 vs 最弱处）。当用户要求论文精读、论文批注、双语对照、论证结构可视化、把英文论文做成可读网页、课程阅读材料、把 PDF/DOCX/链接论文转成 HTML 批注页时使用。也用于在已有批注页上增补段落、调整评注或重排版。
---

# 双栏批注论文

把论文的**论证结构**做成可读的版面：左栏读文本，右栏读论证。产出是**一个自包含的 `.html` 文件**，双击即开。

核心原则：批注是论证工程图，不是读后感。每段必须回答三件事——这段在干什么活、它在链条的哪一环、这一环最容易从哪里断。

## 输入与产出

| 输入 | 处理方式 |
|---|---|
| PDF | 用 `pdf` skill 取文本；保留段落边界，丢掉页眉页脚与参考文献列表 |
| DOCX / TXT / MD | 直接读取；按空行与缩进还原段落 |
| 网页 / DOI 链接 | `web_fetch` 取正文；只取 article body |
| 图片 / 扫描件 | 先 OCR（`pdf` 或图像能力），再核对关键数字 |

产出：`<论文短名>-批注.html`（单文件，CSS/JS 内联），放主项目目录。

**开工前先确认三件事**（缺一项就问，别猜）：批注范围（全文 / 指定章节 / 摘要+引言+结论）、译文深度（逐段全译 / 只译关键段）、课程与作业信息（导航栏要写）。

## 工作流

### Step 0 · 定范围
数清段落规模。全文超过 30 段时，先给用户一个分批方案（按节交付，每节独立成页或以章节为页内 tab），不要一声不响地做完 60 段。

### Step 1 · 抽取原文，锁死段落边界
逐段编号（`§I ¶3`），**原文一个字都不改**——只允许在词句外层包 `<mark>`。删节处用 `[…]` 明示，不得静默合并或改写句子。

### Step 2 · 先画论证地图，再逐段批注
动笔前先写三样：`stages`（问题→论点→证据→反驳→结论的真实走法，允许"先破后立"这类变体）、`core_claim`（一句话）、`strongest / weakest`。
**顺序不能颠倒**：先有地图，批注才知道每段该往哪个方向说。反过来做，右栏会变成逐段读后感，底部总览会与正文打架。

### Step 3 · 逐段三件事
每段产出四个字段：`en`（原文＋高亮）、`zh`（意译）、`func`（段落功能）、`role`（逻辑角色）、`tip`（技巧/漏洞）。写法与判定标准**必须**先读 `references/annotation-rubric.md`——五类高亮的边界、功能词表、意译规则、塌方清单都在那里。

高亮只用这五个类名，不得自造：

```html
<mark class="hl hl-thesis">核心论点</mark>
<mark class="hl hl-concept">关键概念/术语</mark>
<mark class="hl hl-evidence">实证证据/数据</mark>
<mark class="hl hl-concession">让步/反驳处理</mark>
<mark class="hl hl-method">方法论说明</mark>
```

### Step 4 · 写内容 JSON
按节写，一节点一个 `paragraphs` 数组。段落多时可分片：主文件放 `meta`＋`overview`＋前几节，其余节另存 `part2.json`、`part3.json`（只含 `{"sections":[…]}`），构建时用 `--part` 追加。

```json
{
  "meta": {
    "title_en": "The Quiet Power of Indicators",
    "title_zh": "指标的静默权力",
    "course": "法学研究方法 · 第七讲",
    "author": "Davis, K. et al.",
    "year": "2012",
    "source": "Law & Society Review 46(2)",
    "footnote": "（可省略，省略则用默认版权说明）"
  },
  "sections": [
    {
      "id": "sec-1", "num": "I",
      "title_en": "Introduction", "title_zh": "引言",
      "role": "提出问题",
      "paragraphs": [
        {
          "id": "p-1", "label": "核心主张",
          "en": "This article <mark class=\"hl hl-thesis\">argues that rankings govern by shaping what counts as comparable</mark>, while <mark class=\"hl hl-concept\">commensuration</mark> …",
          "zh": "本文认为，排名之所以具有治理效力，是因为它先规定了什么算作可比较的对象……",
          "func": "提出主张", "role": "承接上一段对既有解释的否定，为第二节的概念工具提供落点",
          "tip": "以定义权换取论证空间：先夺走「可比性」的解释权，后续比较研究便只能沿其框架展开"
        }
      ]
    }
  ],
  "overview": {
    "stages": [
      {"stage": "问题", "text": "既有研究把排名视为信息工具，忽略了它的构成性效力"},
      {"stage": "论点", "text": "排名通过「通约」重塑治理对象"},
      {"stage": "证据", "text": "三国法学院排名与拨款数据的对照"},
      {"stage": "反驳", "text": "预先回应「排名只是反映偏好」的批评"},
      {"stage": "结论", "text": "指标治理需要前置的合法性审查"}
    ],
    "core_claim": "……",
    "strongest": "……",
    "weakest": "……"
  }
}
```

### Step 5 · 渲染

```bash
python3 scripts/build.py content.json /path/to/论文-批注.html
# 分片构建：
python3 scripts/build.py content.json out.html --part part2.json --part part3.json
```

脚本校验必填字段、剥离危险标签、按功能自动给批注卡配左色边，并报告五色高亮的数量分布。

### Step 6 · 自检，再交付

```bash
python3 scripts/check_output.py /path/to/论文-批注.html
```

FAIL 必须清零；WARN 里"未出现的维度"只有在论文确实没有这类内容时才可接受（例如纯理论文章没有数据，就没有蓝色）。随后用浏览器看两个宽度：**1280px**（双栏对齐、批注卡不错位）与 **390px**（单栏堆叠、导航条可横滑）。最后用 `present_files` 交付 `.html`。

## 视觉规范

`assets/template.html` 是唯一视觉源：**复制它、填内容，不要重写 CSS**。要改风格只动 `:root` 里的令牌。

| 项 | 值 |
|---|---|
| 顶部导航栏 | 深海军蓝 `#0f2740`；标题 Lora，课程/作者/出处用 IBM Plex Sans 小字 |
| 纸面底色 | 米白 `#faf7f1`，极淡网点 |
| 章节导航 | `position:sticky; top:0`，横滑不换行，当前节下划线加重 |
| 左栏 | 1.58 份宽：英文 Lora → 1px 分隔线 → 中文译文 |
| 中文译文块 | 底 `#f0ece2`、左竖线 3px `#c8bda4`、无高亮、无批注 |
| 右栏 | 1 份宽；批注卡左色边 4px（跟随段落功能）、底 `#f5f2e9` |
| 底部总览 | 同深蓝底；骨架链 → 一句话主张 → 最强/最弱双卡 |
| 断点 | ≤900px 单栏（批注移到译文下方），≤520px 收紧内距 |
| 字体 | 正文 `Lora`＋`Noto Serif SC`；界面 `IBM Plex Sans`；走 `miaoda.feishu.cn/fonts` 镜像，带系统字体兜底 |

五色语义固定，不得调换：黄=thesis、红=concept、蓝=evidence、绿=concession、紫=method。图例必须与正文用色一致，同屏可见。

## 质量红线

交付前逐条过：

1. **段落一一对应**：每个 `.pair` 都有英文、译文、批注三件套，编号连续，顺序与原文章节一致。
2. **原文未改**：英文只多了 `<mark>`，词句、标点、数字、引用格式零改动。
3. **高亮克制**：每 100 词 1–2 处；单段不超过 6 处；一段内不堆三种以上颜色。
4. **批注不注水**：`role` 说清上下游依赖，`tip` 落到具体词句，不写"论证有力/略显不足"。
5. **译文像中文**：拆长句、去被动堆叠、术语全文一致；强度不升格（may → 或可）。
6. **总览自洽**：`stages` 与正文批注指向同一套环节；`strongest/weakest` 指名具体段落，不写泛泛之论。
7. **单文件可用**：无外链 CSS/JS；字体缺失时页面仍成立；打印不失版。

## 资源

- `assets/template.html` —— 完整版式与样式（含 sticky 导航、响应式、打印样式、阅读模式开关）。
- `references/annotation-rubric.md` —— 五维判定标准、功能词表、逻辑角色句式、意译规则、常见塌方。**Step 3 必读**。
- `scripts/build.py` —— JSON → HTML 渲染与字段校验。
- `scripts/check_output.py` —— 结构自检（闭合、锚点、双栏配平、五色图例、断点、字体）。
