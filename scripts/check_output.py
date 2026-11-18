#!/usr/bin/env python3
"""结构自检：交付前跑一遍 build.py 的产物，拦住常见塌方。

用法：python3 check_output.py out.html
仅用标准库；有 FAIL 时退出码为 1。
"""
import re
import sys
from collections import Counter
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ALLOWED_MARK = {"hl-thesis", "hl-concept", "hl-evidence", "hl-concession", "hl-method"}
REQUIRED_LABELS = ["核心论点", "关键概念", "实证证据", "让步", "方法论", "段落", "逻辑角色", "论证技巧"]


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []
        self.ids = []
        self.nav_targets = []
        self.marks = Counter()
        self.pairs = self.lefts = self.zhs = self.notes = self.swatches = 0
        self.legend_items = 0
        self.implicit_p = 0
        self.has_sticky = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "") or ""
        if tag == "div" and "pair" in cls.split():
            self.pairs += 1
        if tag == "div" and "left" in cls.split():
            self.lefts += 1
        if tag == "div" and "zh" in cls.split():
            self.zhs += 1
        if tag == "aside" and "note" in cls.split():
            self.notes += 1
        if "swatch" in cls.split():
            self.swatches += 1
        if tag == "span" and "legend-item" in cls.split():
            self.legend_items += 1
        if tag == "mark":
            for c in cls.split():
                if c.startswith("hl-"):
                    self.marks[c] += 1
        if tag == "a" and d.get("data-target"):
            self.nav_targets.append(d["data-target"])
        if d.get("id"):
            self.ids.append(d["id"])
        if cls and "secnav" in cls.split():
            self.has_sticky = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                dropped = self.stack.pop()
                if dropped in ("p", "li"):
                    self.implicit_p += 1
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"多余的闭合标签 </{tag}>")


def main() -> None:
    path = sys.argv[1]
    src = open(path, encoding="utf-8").read()
    scan = Scan()
    scan.feed(src)

    fails, warns, oks = [], [], []
    if "<!--@" in src:
        fails.append("残留未替换的模板占位符 <!--@…@-->")
    else:
        oks.append("无残留占位符")

    if scan.errors:
        fails.append("标签闭合异常：" + "；".join(scan.errors[:5]))
    if scan.stack:
        fails.append("未闭合标签：" + ", ".join(scan.stack[:8]))
    if not scan.errors and not scan.stack:
        oks.append("标签闭合正常")

    if scan.pairs == 0:
        fails.append("没有 .pair 双栏单元")
    else:
        oks.append(f"双栏单元 {scan.pairs} 个")
    for name, got in ((".left", scan.lefts), (".zh 译文块", scan.zhs), (".note 批注卡", scan.notes)):
        if got != scan.pairs:
            fails.append(f"{name} 数量 {got} ≠ 双栏单元 {scan.pairs}")

    unknown = [k for k in scan.marks if k not in ALLOWED_MARK]
    if unknown:
        fails.append("非法高亮类名：" + ", ".join(unknown))
    if not scan.marks:
        fails.append("全文无高亮标注")
    else:
        oks.append("高亮分布：" + "，".join(f"{k}={v}" for k, v in scan.marks.items()))
        missing = ALLOWED_MARK - set(scan.marks)
        if missing:
            warns.append("未出现的维度（论文确实没有可标注内容才可接受）：" + "、".join(sorted(missing)))

    if scan.swatches != 5 or scan.legend_items != 5:
        fails.append(f"图例应为五类：色块 {scan.swatches}，图例项 {scan.legend_items}")
    else:
        oks.append("五色图例齐全")

    if not scan.has_sticky:
        fails.append("缺少 .secnav 章节导航条")

    if len(set(scan.ids)) != len(scan.ids):
        dup = [k for k, v in Counter(scan.ids).items() if v > 1]
        fails.append("id 重复：" + ", ".join(dup[:5]))

    targets = set(scan.nav_targets)
    missing_targets = [t for t in targets if t not in scan.ids]
    if missing_targets:
        fails.append("导航指向不存在的锚点：" + ", ".join(missing_targets))
    else:
        oks.append(f"章节导航 {len(targets)} 个锚点全部可跳转")

    for label in REQUIRED_LABELS:
        if label not in src:
            fails.append(f"缺少界面文案「{label}」")

    if "@media (max-width:900px)" not in src:
        fails.append("缺少移动端单栏断点")
    if "#f0ece2" not in src.lower():
        fails.append("中文译文块底色应为 #f0ece2")
    if "Lora" not in src or "IBM Plex Sans" not in src:
        fails.append("字体未按规范设置（Lora 正文 / IBM Plex Sans 界面）")
    if "position:sticky" not in src:
        fails.append("导航条未设置 sticky")

    print(f"检查对象：{path}")
    for m in oks:
        print("  PASS " + m)
    for m in warns:
        print("  WARN " + m)
    for m in fails:
        print("  FAIL " + m)
    print(("通过" if not fails else f"未通过，{len(fails)} 项需修") + f"（{scan.pairs} 段）")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
