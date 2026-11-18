#!/usr/bin/env python3
"""把 content.json 渲染成单文件双栏批注 HTML。

用法：
    python3 build.py content.json out.html [--template path/to/template.html]

content.json 结构见 SKILL.md「内容 JSON 契约」。
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ALLOWED_ACCENTS = {"thesis", "concept", "evidence", "concession", "method", "neutral"}

# 段落功能 → 批注卡左色边（五色维度之一）
FUNC_ACCENT = {
    "引出问题": "neutral", "提出问题": "neutral", "交代背景": "neutral", "界定范围": "neutral",
    "提出主张": "thesis", "核心主张": "thesis", "重申论点": "thesis", "总结观点": "thesis", "收束": "thesis",
    "定义概念": "concept", "概念辨析": "concept", "区分术语": "concept", "澄清": "concept",
    "提供证据": "evidence", "举例": "evidence", "数据呈现": "evidence", "案例分析": "evidence",
    "文献回顾": "evidence", "实证检验": "evidence",
    "让步": "concession", "反驳": "concession", "回应异议": "concession", "限定条件": "concession", "预设反驳": "concession",
    "方法说明": "method", "研究设计": "method", "方法论": "method", "分析框架": "method", "样本说明": "method",
}

BAD_TAGS = re.compile(r"<\s*(script|style|iframe|object|embed)\b", re.I)
EVENT_ATTR = re.compile(r"\son\w+\s*=", re.I)
JS_URL = re.compile(r"(href|src)\s*=\s*\"?\s*javascript:", re.I)


def clean_en(raw: str) -> str:
    """英文段落允许 <mark>/<em>/<strong>/<a>/<i>/<br>，其余结构性注入一律剥离。"""
    if BAD_TAGS.search(raw):
        raise SystemExit("content.json 的 en 字段包含禁止的标签（script/style/iframe…）")
    raw = EVENT_ATTR.sub(" data-x=", raw)
    raw = JS_URL.sub(r'\1="#"', raw)
    return raw.strip()


def esc(text: str) -> str:
    return html.escape(str(text).strip(), quote=True)


def accent_of(p: dict) -> str:
    acc = (p.get("accent") or "").strip().lower()
    if acc in ALLOWED_ACCENTS:
        return acc
    func = p.get("func", "").strip()
    if func in FUNC_ACCENT:
        return FUNC_ACCENT[func]
    for key, val in FUNC_ACCENT.items():
        if key in func:
            return val
    return "neutral"


def req(d: dict, key: str, where: str) -> str:
    if not str(d.get(key, "")).strip():
        raise SystemExit(f"{where} 缺少必填字段：{key}")
    return str(d[key]).strip()


def render_pair(sec_num: str, idx: int, p: dict, where: str) -> str:
    accent = accent_of(p)
    func = req(p, "func", where)
    role = req(p, "role", where)
    tip = req(p, "tip", where)
    en = clean_en(req(p, "en", where))
    zh_paras = [req(p, "zh", where)] + [str(x).strip() for x in p.get("zh_extra", []) if str(x).strip()]
    zh_html = "".join(f"<p>{esc(x)}</p>" for x in zh_paras)
    label = p.get("label") or func
    return f"""    <div class="pair" id="{esc(p.get('id', f'p{idx}'))}">
      <div class="pnum-row"><span class="pnum">§{esc(sec_num)} · ¶{idx}</span><span class="pnum-label">{esc(label)}</span></div>
      <div class="left">
        <p class="en">{en}</p>
        <div class="split"></div>
        <div class="zh"><span class="zh-tag">中译 · 意译</span>{zh_html}</div>
      </div>
      <aside class="note note-{accent}">
        <div class="note-funcblock"><span class="note-k">段落功能 · Paragraph Function</span><div class="note-func">{esc(func)}</div></div>
        <div class="note-row"><span class="note-k">逻辑角色 · Logic Role</span><div class="note-v">{esc(role)}</div></div>
        <div class="note-row"><span class="note-k">论证技巧 / 潜在漏洞 · Move &amp; Risk</span><div class="note-v is-tip">{esc(tip)}</div></div>
      </aside>
    </div>
"""


def render_section(sec: dict, i: int) -> tuple[str, str]:
    sid = sec.get("id") or f"sec-{i + 1}"
    num = str(sec.get("num") or i + 1)
    title_en = req(sec, "title_en", f"sections[{i}]")
    title_zh = sec.get("title_zh", "").strip()
    role = sec.get("role", "").strip()
    role_attr = f' data-role="{esc(role)}"' if role else ""
    pairs = "".join(
        render_pair(num, j + 1, p, f"sections[{i}].paragraphs[{j}]")
        for j, p in enumerate(sec.get("paragraphs", []))
    )
    if not pairs:
        raise SystemExit(f"sections[{i}] 没有任何段落")
    head = f"""  <section class="sec" id="{esc(sid)}" data-sec="{esc(sid)}"{role_attr}>
    <div class="sec-head">
      <div class="sec-num">{esc(num)}</div>
      <h2 class="sec-title">{esc(title_en)}</h2>
"""
    if title_zh:
        head += f"      <div class=\"sec-title-zh\">{esc(title_zh)}</div>\n"
    if role:
        head += f"      <div class=\"sec-role\">{esc(role)}</div>\n"
    head += "    </div>\n"
    return head + pairs + "  </section>\n", f'<a href="#{esc(sid)}" data-target="{esc(sid)}">{esc(num)} · {esc(title_zh or title_en)}</a>'


def render_chain(stages: list) -> str:
    if not stages:
        raise SystemExit("overview.stages 为空")
    out = []
    for k, st in enumerate(stages):
        stage = req(st, "stage", "overview.stages")
        text = req(st, "text", "overview.stages")
        out.append(f'<div class="step"><div class="step-k">{esc(stage)}</div><div class="step-v">{esc(text)}</div></div>')
        if k < len(stages) - 1:
            out.append('<div class="arrow" aria-hidden="true">→</div>')
    return "".join(out)


def build(content: dict, template: str) -> str:
    meta = content.get("meta", {})
    title_en = req(meta, "title_en", "meta")
    title_zh = req(meta, "title_zh", "meta")
    course = req(meta, "course", "meta")

    meta_bits = [f"<span><b>课程</b> {esc(course)}</span>"]
    if meta.get("author"):
        meta_bits.append(f"<span><b>作者</b> {esc(meta['author'])}</span>")
    if meta.get("year"):
        meta_bits.append(f"<span><b>年份</b> {esc(meta['year'])}</span>")
    if meta.get("source"):
        meta_bits.append(f"<span><b>出处</b> {esc(meta['source'])}</span>")
    counts = content.get("meta", {})
    n_para = sum(len(s.get("paragraphs", [])) for s in content.get("sections", []))
    meta_bits.append(f"<span><b>批注规模</b> {len(content.get('sections', []))} 节 / {n_para} 段</span>")

    body, nav = [], []
    for i, sec in enumerate(content.get("sections", [])):
        s_html, s_nav = render_section(sec, i)
        body.append(s_html)
        nav.append(s_nav)
    nav.append('<span class="sep" aria-hidden="true">|</span><a href="#overview" data-target="overview">总览</a>')

    ov = content.get("overview", {})
    footnote = meta.get("footnote") or (
        "英文原文版权归原作者与出版方所有，此处仅作课程阅读使用；中文译文为教学用意译，"
        "段落批注为阅读分析，非作者本人观点。高亮只标出论证坐标，完整语义请以原文为准。"
    )

    out = template
    repl = {
        "<!--@DOC_TITLE@-->": esc(f"{title_en} · 双栏批注本"),
        "<!--@TITLE_EN@-->": esc(title_en),
        "<!--@TITLE_ZH@-->": esc(title_zh),
        "<!--@META@-->": "".join(meta_bits),
        "<!--@SECNAV@-->": "".join(nav),
        "<!--@CONTENT@-->": "\n".join(body),
        "<!--@CHAIN@-->": render_chain(ov.get("stages", [])),
        "<!--@CORE_CLAIM@-->": esc(req(ov, "core_claim", "overview")),
        "<!--@STRONGEST@-->": esc(req(ov, "strongest", "overview")),
        "<!--@WEAKEST@-->": esc(req(ov, "weakest", "overview")),
        "<!--@FOOTNOTE@-->": esc(footnote),
    }
    for token, value in repl.items():
        if token not in out:
            raise SystemExit(f"模板缺少占位符 {token}")
        out = out.replace(token, value)
    return out, n_para


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("output")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "assets" / "template.html"))
    ap.add_argument("--part", action="append", default=[], help="追加分片（仅含 sections），可重复")
    args = ap.parse_args()

    data = json.loads(Path(args.content).read_text(encoding="utf-8"))
    for extra in args.part:
        part = json.loads(Path(extra).read_text(encoding="utf-8"))
        data.setdefault("sections", []).extend(part.get("sections", []))
    tpl = Path(args.template).read_text(encoding="utf-8")
    html_out, n_para = build(data, tpl)
    Path(args.output).write_text(html_out, encoding="utf-8")
    marks = {k: html_out.count(f'hl hl-{k}') for k in ("thesis", "concept", "evidence", "concession", "method")}
    print(f"OK  {args.output}  sections={len(data.get('sections', []))} paragraphs={n_para}")
    print("marks " + "  ".join(f"{k}={v}" for k, v in marks.items()))
    if sum(marks.values()) == 0:
        print("WARN 全文没有高亮；请检查 en 字段里的 <mark class=\"hl hl-…\"> 标注", file=sys.stderr)


if __name__ == "__main__":
    main()
