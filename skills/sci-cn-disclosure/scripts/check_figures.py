#!/usr/bin/env python3
"""附图标记与附图说明的双向核对。

两条规则来自《专利审查指南》对附图的要求,但真正的用途在交底书阶段:标记与正文一旦
对不上,代理师转写正式申请文件时会把错误原样带过去,而附图标记是审查员最容易逐个核对
的东西之一。

核对四件事:

1. 附图说明里声明的图号,与正文引用的图号一致(有图未说明 / 说明了不存在的图)
2. 每个附图标记 `N—部件名称` 都在说明书正文中被提及
3. 同一编号在全文只对应一个部件名称(不同名称共用一个号,是代理师最常踩的坑)
4. 标记编号连续,无跳号

用法:
    python check_figures.py 交底书.md
    python check_figures.py 交底书.docx --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 校验器互相 import 会在技能目录里留下 __pycache__。短命 CLI 不需要字节码缓存，
# 关掉它，技能目录保持干净(打包时也就不会混进 .pyc)。
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
from read_source import read_disclosure  # noqa: E402

# 附图标记的引入形式:`1—原料储罐`。只认全角破折号——ASCII 连字符会把
# `4-mer`、`1 - \cos(...)` 这类误判成标记定义。
NUMERAL_DEF = re.compile(r'(?<![\d])(\d{1,3})\s*[—－]\s*([^；;，,。\n）)]{2,20})')
# 附图说明里的图号声明:`图1为……`
FIG_DECL = re.compile(r'(?m)^图\s*(\d{1,2})\s*[为是]')
# 正文里对图的引用:`（图 3）`、`见图 3`、`如图 3 所示`
FIG_REF = re.compile(r'图\s*(\d{1,2})')
# 曾经这里有一张"数量单位"黑名单，用来把 `81 bp` 这类数值排除在附图标记之外。
# 那张表只列了某一个领域的单位:换到机械类，`间隙 5 mm` 里的 5 就被当成对标记 5 的
# 提及，该报的 NUMERAL_NOT_IN_TEXT 一条都不报。单位列不完，黑名单就永远是个
# 随领域失效的隐藏假设。现在改为按声明的部件名称锚定(见 mentions_numeral)，
# 一个单位都不必认识。
# 交底书末尾插入的图片:![图N](figures/figN.png)
IMG = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
# spec 里写 x_1 会原样渲染成字面下划线；必须写 x_{1} 才会排成真下标。
# 只认后面直接跟字母数字的下划线/上标符，`t_{next}`、`5′→3′`、`k-mer` 都不算。
RAW_SCRIPT = re.compile(r'[A-Za-zα-ωΑ-Ωℓγθμσ][_^](?!\{)[A-Za-z0-9]')


def section(text: str, head: str, nxt: str | None = None) -> str:
    m = re.search(rf'(?m)^#*\s*\**\s*{head}\s*\**\s*$', text)
    if not m:
        return ''
    rest = text[m.end():]
    if nxt:
        s = re.search(rf'(?m)^#*\s*\**\s*{nxt}\s*\**\s*$', rest)
        if s:
            rest = rest[:s.start()]
    return rest



def name_tokens(name: str) -> set[str]:
    """部件名称的比对令牌:汉字 2-gram + 拉丁词。

    正文里名称常被缩写(声明「Transformer 编码块」，正文写「Transformer 块 13」)，
    所以不能要求整名相等;2-gram 与拉丁词能吃下这种缩写。
    """
    toks = {t for t in re.findall(r'[A-Za-z][A-Za-z0-9\-]*', name)}
    for run in re.findall(r'[一-鿿]+', name):
        toks |= {run[i:i + 2] for i in range(max(1, len(run) - 1))} if len(run) > 1 else {run}
    return toks


def mentions_numeral(body: str, num: int, name: str, window: int = 12) -> bool:
    """正文里有没有以「部件名称 + 编号」的形式提到过这个标记。

    判据是编号**紧邻的前文**里出现该名称的痕迹，而不是全文任意位置出现过名称
    ——「本装置采用复位弹簧」加上别处的「间隙 5 mm」，不构成对标记 5 的提及。
    """
    toks = name_tokens(name)
    if not toks:
        return False
    for m in re.finditer(rf'(?<!\d){num}(?!\d)', body):
        prefix = body[max(0, m.start() - window):m.start()]
        if any(t in prefix for t in toks):
            return True
    return False


def check(text: str, src: Path | None = None) -> list[tuple[str, str, str]]:
    f: list[tuple[str, str, str]] = []

    def add(sev, code, msg):
        f.append((sev, code, msg))

    spec = text.split('说明书', 1)[-1]
    decl_sec = section(text, '附图说明', '具体实施方式')
    body = section(text, '具体实施方式') or spec
    # 标记声明行(`5—复位弹簧`)本身不算「正文提及」——不剔掉的话，每个标记都会因为
    # 自己的声明而被判成「出现过」，报错就指错了地方。
    flat_body = re.sub(r'\s+', '', NUMERAL_DEF.sub('', body))

    # --- 1. 图号:声明 vs 引用 ---
    declared = {int(n) for n in FIG_DECL.findall(decl_sec)}
    if not declared:
        add('WARNING', 'NO_FIGURE_DECL', '未找到「附图说明」小节，或其中没有“图N为……”的声明。')
    else:
        if sorted(declared) != list(range(1, len(declared) + 1)):
            add('ERROR', 'FIGURE_SEQUENCE', f'附图编号不连续：{sorted(declared)}。')
        # 声明了图，就必须真的有图。附图说明写得再全，没有图仍是不完整的交底书。
        imgs = IMG.findall(text)
        if not imgs:
            add('ERROR', 'NO_FIGURE_FILES',
                f'附图说明声明了 {len(declared)} 幅图，但文中没有任何图片引用。'
                f'请在文末「附图」一节以 ![图N](路径) 插入图片。')
        elif src is not None:
            missing = [i for i in imgs if not (src.parent / i).exists()]
            if missing:
                add('ERROR', 'FIGURE_FILE_MISSING', f'图片文件不存在：{missing}。')
            if len(imgs) < len(declared):
                add('ERROR', 'FIGURE_FILE_COUNT',
                    f'附图说明声明 {len(declared)} 幅图，实际只插入 {len(imgs)} 幅。')

        referenced = {int(n) for n in FIG_REF.findall(body)}
        for n in sorted(referenced - declared):
            add('ERROR', 'FIGURE_NOT_DECLARED', f'正文引用了图 {n}，但附图说明中没有该图。')
        for n in sorted(declared - referenced):
            add('WARNING', 'FIGURE_NEVER_REFERENCED',
                f'图 {n} 已在附图说明中声明，但具体实施方式中从未引用。')

    # --- 2/3. 附图标记 ---
    # 正文中标记的使用形式是「去噪网络 3」——部件名在前、编号在后。判定按名称锚定:
    # 编号紧邻的前文里要出现该名称的痕迹。这条同时把写作规则变成了可校验的东西。
    defs: dict[int, set[str]] = {}
    for num, name in NUMERAL_DEF.findall(text):
        defs.setdefault(int(num), set()).add(name.strip())
    if not defs:
        add('WARNING', 'NO_NUMERALS', '未找到 `N—部件名称` 形式的附图标记。')
        return f

    for num, names in sorted(defs.items()):
        if len(names) > 1:
            add('ERROR', 'NUMERAL_CONFLICT',
                f'标记 {num} 对应多个名称：{sorted(names)}。同一编号在全文只能指一个部件。')
        name = sorted(names)[0]
        if not any(mentions_numeral(flat_body, num, n) for n in names):
            if any(t in flat_body for n in names for t in name_tokens(n)):
                add('ERROR', 'NUMERAL_NOT_ANCHORED',
                    f'标记 {num}「{name}」在正文出现过，但没有一处写成「{name} {num}」'
                    f'这种名称紧接编号的形式。附图标记靠这个形式与正文绑定，'
                    f'散落的名称起不到绑定作用。')
            else:
                add('ERROR', 'NUMERAL_NOT_IN_TEXT',
                    f'标记 {num}「{name}」未在说明书文字部分被提及。'
                    f'未提及的标记不得出现在附图中。')

    nums = sorted(defs)
    missing = [n for n in range(1, max(nums) + 1) if n not in defs]
    if missing:
        add('WARNING', 'NUMERAL_GAP', f'附图标记编号跳号，缺：{missing}。')

    # --- 4. spec 里的下标写法 ---
    # 只扫标签文本。整份 JSON 扫会把 text_color、from_xy 这类键名也算成下标。
    if src is not None:
        for spec in sorted((src.parent / 'figures' / 'specs').glob('fig*.json')):
            try:
                j = json.loads(spec.read_text(encoding='utf8'))
            except json.JSONDecodeError:
                add('ERROR', 'SPEC_INVALID', f'{spec.name} 不是合法 JSON。')
                continue
            texts = [str(n.get('label', '')) for n in j.get('nodes', [])]
            texts += [str(l.get('text', '')) for l in j.get('labels', [])]
            texts += [str(fb.get('label', '')) for fb in j.get('feedback', [])]
            texts.append(str(j.get('title', '')))
            bad = sorted({m for t in texts for m in RAW_SCRIPT.findall(t)})
            if bad:
                add('ERROR', 'RAW_SUBSCRIPT',
                    f'{spec.name} 中的下标未加花括号：{bad}。'
                    f'写作 x_{{1}} 才会排成真下标，写 x_1 会原样渲染成字面下划线。')

    # --- 5. 名称复用 ---
    by_name: dict[str, set[int]] = {}
    for num, names in defs.items():
        for name in names:
            by_name.setdefault(re.sub(r'\s+', '', name), set()).add(num)
    for name, nums_ in by_name.items():
        if len(nums_) > 1:
            add('ERROR', 'NAME_CONFLICT',
                f'部件「{name}」被赋予多个标记：{sorted(nums_)}。同一部件在各图中编号须一致。')
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description='附图标记与附图说明核对')
    ap.add_argument('disclosure')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    src = Path(a.disclosure)
    findings = check(read_disclosure(src), src)

    if a.json:
        print(json.dumps([{'severity': s, 'code': c, 'message': m} for s, c, m in findings],
                         ensure_ascii=False, indent=2))
    else:
        for s, c, m in findings:
            print(f'{s}\t{c}\t{m}')
        errs = sum(1 for s, *_ in findings if s == 'ERROR')
        if findings:
            print(f'\n汇总: {errs} 个错误，{len(findings) - errs} 个警告')
        else:
            print('PASS: 附图编号与附图标记均与正文一致。')
    return 1 if any(s == 'ERROR' for s, *_ in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
