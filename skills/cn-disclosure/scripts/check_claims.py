#!/usr/bin/env python3
"""交底书「权利要求书」一节的结构检查。

直接读交底书,不经中间 JSON——所以代理师回稿转成 Markdown 后也能照跑。

相对通用的权项审计器有两处改动,都是中文权项写法需要的:Markdown 粗体编号
(`**1.**`),以及子步骤编号(`2.1）`)不得被误判成权项边界。
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

# A claim starts at line-start with N. — but 2.1） is a sub-step, not claim 2.
CLAIM_START = re.compile(r'(?m)^\s*\*{0,2}(\d{1,2})\s*[.．]\s*\*{0,2}(?!\d)')
REF = re.compile(r'权利要求\s*(\d+)(?:\s*(?:至|到|-|—|~)\s*(\d+))?')
# 所述X — 中文名词短语没有分隔符，贪心捕获会把整句吞掉。先粗捕，再由
# narrow() 收敛到真正复现的术语；"根据权利要求1所述的…" 里的"所述的"不是术语引用。
TERM = re.compile(r'所述(?!的)([一-鿿A-Za-z0-9]{2,16})')
PLACEHOLDER = re.compile(r'[\[【](?:TO CONFIRM|待确认)[^\]】]*[\]】]', re.I)
PROMO = re.compile(r'效果更好|性能优异|显著提高|大大提高|明显优于|最佳|最优|远超')
VAGUE_END = re.compile(r'(设计结果|技术结果|处理结果|最终结果)\s*[。.]?\s*$')
GENERIC = {'方法', '装置', '设备', '系统', '步骤', '程序', '模型', '参数', '数据',
           '方法的步骤', '计算机程序', '处理器'}
# 收敛后若仍以动词性/结构性字收尾，说明还是过捕获，判不了前置基础
TAIL_NOISE = tuple('为被是由中后前时即又并和与或的了着过等')


def extract_claims(text: str) -> list[tuple[int, str]]:
    """Return [(number, body)] for the 权利要求书 section."""
    m = re.search(r'(?m)^#*\s*权利要求书\s*$', text)
    if m:
        rest = text[m.end():]
        stop = re.search(r'(?m)^#*\s*说明书\s*$', rest)
        rest = rest[:stop.start()] if stop else rest
    else:
        rest = text
    marks = list(CLAIM_START.finditer(rest))
    out = []
    for i, mk in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(rest)
        out.append((int(mk.group(1)), rest[mk.end():end].strip()))
    return out


def narrow(raw: str, corpus: str) -> str | None:
    """Longest prefix of a greedy 所述X capture that recurs in the claims.

    A phrase that appears only once is almost certainly an over-capture spanning a
    verb, not a term whose antecedent basis can be judged.
    """
    for n in range(min(len(raw), 12), 1, -1):
        p = raw[:n]
        if corpus.count(p) >= 2:
            return p
    return None


def audit(claims: list[tuple[int, str]]) -> list[tuple[str, str, str, str]]:
    f: list[tuple[str, str, str, str]] = []

    def add(sev, num, code, msg):
        f.append((sev, num, code, msg))

    if not claims:
        add('ERROR', '整体', 'NO_CLAIMS', '未识别到任何权利要求。')
        return f

    numbers = [n for n, _ in claims]
    if numbers != list(range(1, len(numbers) + 1)):
        add('ERROR', '整体', 'NUMBER_SEQUENCE',
            f'编号应连续为 {list(range(1, len(numbers) + 1))}，实际为 {numbers}。')

    bodies = {n: b for n, b in claims}
    corpus = re.sub(r'\s+', '', ''.join(bodies.values()))
    seen = ''
    for num, body in claims:
        tag = f'权利要求{num}'
        compact = re.sub(r'\s+', '', body)

        if not compact:
            add('ERROR', tag, 'EMPTY_CLAIM', '权利要求正文为空。')
            continue
        if PLACEHOLDER.search(body):
            add('ERROR', tag, 'PLACEHOLDER', '正式权利要求中仍含待确认标记。')

        refs = []
        for a, b in REF.findall(body):
            refs.extend(range(int(a), int(b) + 1) if b else [int(a)])
        if num == 1:
            if refs:
                add('ERROR', tag, 'INDEP_REFERENCES', '权利要求 1 不应引用其他权利要求。')
        elif not refs:
            add('WARNING', tag, 'NO_REFERENCE', '未检测到从属引用；确认其是否为独立权利要求。')
        for r in refs:
            if r >= num:
                add('ERROR', tag, 'FORWARD_REFERENCE', f'引用了非在先的权利要求 {r}。')
            elif r not in bodies:
                add('ERROR', tag, 'UNKNOWN_REFERENCE', f'引用的权利要求 {r} 不存在。')

        if '其特征在于' not in compact:
            add('WARNING', tag, 'TRANSITION', '未检测到"其特征在于"过渡语。')
        if PROMO.search(compact):
            add('WARNING', tag, 'PROMO_LANGUAGE', '含宣传性措辞，确认是否改为技术限定。')
        if num == 1 and VAGUE_END.search(compact):
            add('ERROR', tag, 'VAGUE_FINAL_RESULT',
                '独立权利要求以模糊结果收尾，应落到具体产物或控制动作。')
        if len(compact) < 40:
            add('WARNING', tag, 'TOO_SHORT', '权利要求较短，确认是否完整限定技术方案。')

        # antecedent basis: 所述X must have been introduced earlier or in a cited claim
        basis = seen + ''.join(bodies.get(r, '') for r in refs)
        basis = re.sub(r'\s+', '', basis)
        reported: set[str] = set()
        for raw in sorted(set(TERM.findall(body))):
            t = narrow(raw, corpus)
            if not t or t in GENERIC or t in reported or t.endswith(TAIL_NOISE):
                continue
            reported.add(t)
            # 先在本权项内被引入（不带"所述"出现过）也算有基础
            introduced = re.search(rf'(?<!所述){re.escape(t)}', compact)
            if t not in basis and not introduced:
                add('WARNING', tag, 'ANTECEDENT_BASIS', f'术语"{t}"可能缺少清晰的前置基础。')
        seen += body
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description='权利要求书结构检查（中文交底书 Markdown）')
    ap.add_argument('disclosure', help='交底书 Markdown 文件')
    ap.add_argument('--json', action='store_true', help='以 JSON 输出')
    a = ap.parse_args()

    text = read_disclosure(a.disclosure)
    claims = extract_claims(text)
    findings = audit(claims)

    if a.json:
        print(json.dumps([{'severity': s, 'claim': n, 'code': c, 'message': m}
                          for s, n, c, m in findings], ensure_ascii=False, indent=2))
    else:
        for s, n, c, m in findings:
            print(f'{s}\t{n}\t{c}\t{m}')
        errs = sum(1 for s, *_ in findings if s == 'ERROR')
        warns = len(findings) - errs
        if findings:
            print(f'\n汇总: 共 {len(claims)} 项权利要求，{errs} 个错误，{warns} 个警告')
        else:
            print(f'PASS: 共 {len(claims)} 项权利要求，未发现结构性问题。')
    return 1 if any(s == 'ERROR' for s, *_ in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
