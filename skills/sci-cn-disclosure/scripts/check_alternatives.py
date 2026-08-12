#!/usr/bin/env python3
"""枚举交底书里的具体技术选择,并核对可替代实施方式台账。

防两种失败:

1. **编造替代方案。** 写"X 也可以是 Y",而 Y 既没跑过也推不出,会触发第 26.3 条
   公开不充分——后果比保护范围写窄严重得多。每条都带状态,`speculative` 不得进正文。
2. **漏掉替代方案。** 第 33 条不许申请日后增加内容,现在没写的以后永远补不进来。
   所以具体选择从文档里**机械抽取**,不靠回忆。

用法:
    python check_alternatives.py 交底书.md alternatives.json --extract   # 生成待办清单
    python check_alternatives.py 交底书.md alternatives.json             # 校验
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

VALID_STATUS = {'tested', 'derivable', 'routine', 'speculative'}
WRITABLE = {'tested', 'derivable', 'routine'}
ALT_SECTION = re.compile(r'(?m)^#*\s*\**\s*可替代实施方式\s*\**\s*$')
# 交底书里表达"还可以是别的"的常见句式
ALT_PHRASE = re.compile(
    r'(?:还可以|亦可|也可以|可替换为|可以替换成|不限于|均可替代|可采用其他|或其他)[^。；]{0,80}')
# 设计选择 = 带计量单位的数，或被赋值动词引出的数。裸数（步骤编号 1）、公式常数、
# 区间 [0,1] 不是设计选择，全部排除。
#
# 单位用**模式**匹配，不用枚举:数字后紧跟 1–4 个拉丁字母或度量符号（mm/kg/MPa/bp/
# mL/Hz/℃…），或一个中文量词。早先这里是一张枚举表，只列了某个领域的单位，换到机械
# 或化学类就抽不出带单位的设计选择——而漏掉的选择在第 33 条之下再也补不回来。
# 单个拉丁字母只认公认单位符号——否则「阶段 2a」里的 a 会被当成单位。
UNIT = (r'%|‰|℃|°|[A-Za-zµμΩ]{2,4}(?![A-Za-z])'
        r'|[mgLstVAWNJKΩ](?![A-Za-z])'
        r'|[个层维步条次倍轮位种类张项件根台组页万千]')
ASSIGN = r'取|为|是|达|约|等于|不少于|不超过|不低于|不高于|至少|至多|设为|置为'
NUMERIC = re.compile(
    rf'(?:(?<=[{ASSIGN.replace("|", "")}])\s*)?'
    rf'(?<![\d.\-−=（(\[])(\d+(?:\.\d+)?)\s*({UNIT})?')
# 数字后紧跟这些字符的，是编号或公式，不是选择
NOT_CHOICE_AFTER = ('）', ')', ']', '=', '．')


TRIGGER = re.compile(r'^(?:还可以采用|还可以取|还可以是|可替换为|可以替换成|亦可替换为|'
                     r'亦可采用|亦可按|亦可非|还可以|不限于|均可替代|可采用其他|亦可|也可以|或其他)')


def norm(s: str) -> str:
    return re.sub(r'\s+', '', str(s))


def cores(s: str) -> list[str]:
    """Comparison tokens for a phrase.

    Ledger wording and body wording are paraphrases of each other, so whole-prefix
    comparison misfires in both directions. Chinese has no word boundaries, so a
    whole CJK run is one useless token — emit overlapping 4-grams instead, plus
    latin identifiers. Bare digits are dropped: a number matches somewhere in any
    long document and discriminates nothing.
    """
    s = TRIGGER.sub('', norm(s))
    toks: list[str] = []
    for run in re.findall(r'[一-鿿]+', s):
        toks += [run] if len(run) <= 4 else [run[i:i + 4] for i in range(len(run) - 3)]
    toks += re.findall(r'[A-Za-z][A-Za-z0-9.\-]{1,}', s)
    return toks


def covered(phrase: str, haystack: str, ratio: float = 0.25) -> bool:
    """台账措辞与正文措辞是彼此的转述，判定要宽。

    阈值定得高会逼出一个坏结果:为了消警告，把正文原句抄进台账。抄完台账就成了正文的
    副本——它本来是用来独立核对正文的，同源之后核对不出任何东西。反过来为过检去改正文
    措辞，更是让校验器改写稿子。

    所以这里只求"这条登记在正文里有对应物"这种弱信号，命中四分之一即可;真正判断
    "写全了没有"是人的活，校验器只负责把可能漏掉的挑出来看一眼。
    """
    c = cores(phrase)
    if not c:
        return True
    return sum(1 for t in c if t in haystack) / len(c) >= ratio


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


def extract_choices(text: str) -> list[dict]:
    """Numeric literals and alternative phrasings that need a disposition."""
    claims = section(text, '权利要求书', '说明书') or text
    embod = section(text, '具体实施方式', '说明书摘要')
    out, seen = [], set()

    for name, body in (('权利要求书', claims), ('具体实施方式', embod)):
        flat = re.sub(r'[ \t]+', '', body)
        for m in NUMERIC.finditer(flat):
            val, unit = m.group(1), m.group(2) or ''
            after = flat[m.end():m.end() + 1]
            before = flat[max(0, m.start() - 3):m.start()]
            if after in NOT_CHOICE_AFTER:
                continue
            # 必须带单位，或由赋值动词引出
            if not unit and not re.search(ASSIGN, before):
                continue
            ctx = flat[max(0, m.start() - 16):m.end() + 8].replace('\n', '')
            key = val + unit + ctx[-20:]
            if key in seen:
                continue
            seen.add(key)
            out.append({'kind': 'numeric', 'value': val + unit, 'locus': name, 'context': ctx})

    alt = section(text, '可替代实施方式', '补充说明')
    for m in ALT_PHRASE.finditer(alt):
        s = re.sub(r'\s+', '', m.group(0))
        if s not in seen:
            seen.add(s)
            out.append({'kind': 'alternative-sentence', 'locus': '可替代实施方式', 'context': s})
    return out


def check(text: str, data: dict) -> list[tuple[str, str, str]]:
    f: list[tuple[str, str, str]] = []

    def add(sev, code, msg):
        f.append((sev, code, msg))

    choices = data.get('choices', [])
    if not choices:
        add('ERROR', 'NO_CHOICES', 'alternatives.json 的 choices 为空。')

    flat = re.sub(r'\s+', '', text)
    ids: set[str] = set()
    registered_alts: list[str] = []
    parked: list[str] = []          # 正确排除的 speculative，汇总成一条

    for c in choices:
        cid = str(c.get('id', ''))
        if not cid:
            add('ERROR', 'CHOICE_ID', '存在缺少 id 的条目。')
            continue
        if cid in ids:
            add('ERROR', 'DUPLICATE_ID', f'条目 id 重复：{cid}。')
        ids.add(cid)

        if not str(c.get('choice', '')).strip():
            add('ERROR', 'EMPTY_CHOICE', f'{cid} 的 choice 为空。')
        if not str(c.get('locus', '')).strip():
            add('WARNING', 'NO_LOCUS', f'{cid} 未记录 locus（该选择出现在文中何处）。')

        disp = c.get('disposition')
        if disp not in {'alternative', 'essential'}:
            add('ERROR', 'DISPOSITION', f'{cid} 的 disposition 非法：{disp!r}。')
            continue

        if disp == 'essential':
            if not str(c.get('reason', '')).strip():
                add('ERROR', 'NO_REASON', f'{cid} 标为 essential 但未说明为何不可替换。')
            continue

        status = c.get('status')
        if status not in VALID_STATUS:
            add('ERROR', 'STATUS', f'{cid} 的 status 非法：{status!r}。')
            continue
        basis = str(c.get('basis', '')).strip()
        if not basis:
            add('ERROR', 'NO_BASIS', f'{cid} 缺少 basis。')
        elif len(basis) < 12 or basis in {'本领域常规手段', '常规技术'}:
            add('WARNING', 'WEAK_BASIS', f'{cid} 的 basis 过于空泛：“{basis}”。')

        alts = c.get('alternatives', [])
        if not alts:
            add('ERROR', 'NO_ALTERNATIVES', f'{cid} 标为 alternative 但未列出替代方案。')
        registered_alts.extend(alts)

        # 核心门禁：speculative 不得出现在正文
        if status == 'speculative':
            # 严格:被删除的表述应当整条不在正文，用去空白的精确子串判定，不做近似
            present = [a for a in alts if norm(a) in flat]
            if present:
                add('ERROR', 'SPECULATIVE_IN_TEXT',
                    f'{cid} 标为 speculative，但其替代方案已写入正文：{present}。'
                    f'应删除、补实验升级为 tested，或改写为可推导的更弱表述。')
            else:
                parked.append(cid)
        elif status in WRITABLE:
            missing = [a for a in alts if not covered(a, flat)]
            if missing:
                add('WARNING', 'ALT_NOT_IN_TEXT',
                    f'{cid} 的替代方案未在正文出现：{missing}（可写而未写，范围白丢）。')

    # 逐条报"你做对了"会把警告栏刷满，人就学会了忽略警告。合成一条，且给出动作。
    if parked:
        add('WARNING', 'SPECULATIVE_PARKED',
            f'{len(parked)} 条 speculative 已正确排除在正文之外（{"、".join(parked)}）。'
            f'交付前确认这几块保护范围确实拿不到——补得出实验或推理链的，升级后仍可写入。')

    # 反向：正文里出现的替代句式是否都已登记
    alt_body = section(text, '可替代实施方式', '补充说明')
    if not alt_body.strip():
        add('WARNING', 'NO_ALT_SECTION', '交底书中未找到「可替代实施方式」小节。')
    else:
        registry = re.sub(r'\s+', '', ' '.join(
            str(a) for a in registered_alts) + ' '.join(
            str(c.get('choice', '')) + str(c.get('basis', '')) for c in choices))
        for m in ALT_PHRASE.finditer(alt_body):
            s = re.sub(r'\s+', '', m.group(0))
            if not covered(s, registry, 0.2):
                add('WARNING', 'UNREGISTERED_ALT',
                    f'正文这句替代表述在台账里找不到对应条目，请确认：“{s[:40]}…”。'
                    f'（措辞不同不要紧，台账不必抄正文原句；缺条目才要紧。）')

    # 覆盖率：抽取到的数值选择是否都有处置
    # 覆盖率。只查**权利要求里**的数值:它们是保护范围的限定，必须逐个处置。
    # 实施例里的数值多为事实（样本数、实测参数量、算出来的边界），事实没有"替代方案"
    # 可言，由补充说明的兜底段覆盖即可。二者混在一起会让本项永远非零，而永远非零的
    # 警告等于没有警告，只会训练出忽略校验器的习惯。
    disposed = re.sub(r'\s+', '', ' '.join(
        str(c.get('choice', '')) + str(c.get('locus', '')) + str(c.get('basis', ''))
        for c in choices))
    numerics = [ch for ch in extract_choices(text)
                if ch['kind'] == 'numeric' and ch['locus'] == '权利要求书']
    bare = lambda v: re.match(r'[\d.]+', v).group(0)
    uncovered = [ch for ch in numerics if bare(ch['value']) not in disposed]
    if uncovered:
        vals = sorted({c['value'] for c in uncovered})
        add('WARNING', 'UNDISPOSED_CLAIM_VALUES',
            f'权利要求中有 {len(vals)} 个数值未在台账中处置：{vals}。'
            f'权项数值是保护范围的限定，每个都要么标 essential，要么给出替代方案。')
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description='具体选择枚举与可替代实施方式台账校验')
    ap.add_argument('disclosure')
    ap.add_argument('ledger', nargs='?', help='alternatives.json（--extract 时可省略）')
    ap.add_argument('--extract', action='store_true', help='输出待处置的具体选择清单')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    text = read_disclosure(a.disclosure)

    if a.extract:
        ch = extract_choices(text)
        if a.json:
            print(json.dumps(ch, ensure_ascii=False, indent=2))
        else:
            print(f'抽取到 {len(ch)} 个待处置的具体选择：\n')
            for c in ch:
                if c['kind'] == 'numeric':
                    print(f"  [数值] {c['value']:<8} @{c['locus']}  …{c['context']}…")
                else:
                    print(f"  [替代句] @{c['locus']}  {c['context'][:60]}…")
        return 0

    if not a.ledger:
        ap.error('校验模式需要 alternatives.json')
    data = json.loads(Path(a.ledger).read_text(encoding='utf8'))
    findings = check(text, data)

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
            print('PASS: 每个具体选择均已处置，且无 speculative 条目写入正文。')
    return 1 if any(s == 'ERROR' for s, *_ in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
