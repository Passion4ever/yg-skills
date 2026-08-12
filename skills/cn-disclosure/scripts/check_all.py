#!/usr/bin/env python3
"""一条命令跑完全部校验，汇总结果。

分成五条命令手敲时漏掉过其中一条，而且漏了不会有人知道。门禁应当是二元的:
一条命令、一个退出码。

用法:
    python check_all.py 交底书.md
    python check_all.py 交底书.md --evidence evidence.json --alternatives alternatives.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
# 校验器互相 import 会在技能目录里留下 __pycache__。短命 CLI 不需要字节码缓存，
# 关掉它，技能目录保持干净(打包时也就不会混进 .pyc)。
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

from read_source import read_disclosure          # noqa: E402
import check_claims, check_evidence, check_alternatives, check_figures, check_complete  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description='交底书全套校验')
    ap.add_argument('disclosure')
    ap.add_argument('--evidence', default='evidence.json')
    ap.add_argument('--alternatives', default='alternatives.json')
    ap.add_argument('--quiet', action='store_true', help='只列错误，不列警告')
    a = ap.parse_args()

    src = Path(a.disclosure)
    text = read_disclosure(src)
    ev, alt = src.parent / a.evidence, src.parent / a.alternatives

    runs: list[tuple[str, list]] = [
        ('完整性', check_complete.check(src)),
        ('权项结构', [(s, str(n), c + '  ' + m)
                      for s, n, c, m in check_claims.audit(check_claims.extract_claims(text))]),
        ('附图', check_figures.check(text, src)),
    ]
    if ev.exists():
        runs.append(('证据台账',
                     check_evidence.check(text, json.loads(ev.read_text(encoding='utf8')))))
    else:
        runs.append(('证据台账', [('ERROR', 'NO_LEDGER', f'{ev.name} 不存在。')]))
    if alt.exists():
        runs.append(('可替代实施方式',
                     check_alternatives.check(text, json.loads(alt.read_text(encoding='utf8')))))
    else:
        runs.append(('可替代实施方式', [('ERROR', 'NO_LEDGER', f'{alt.name} 不存在。')]))

    total_e = total_w = 0
    for name, findings in runs:
        e = sum(1 for s, *_ in findings if s == 'ERROR')
        w = len(findings) - e
        total_e, total_w = total_e + e, total_w + w
        mark = '✗' if e else ('!' if w else '✓')
        print(f'{mark} {name:<14} {e} 错误 {w} 警告')
        # 警告也要打出来。交付契约 §5 要求逐条过，只报个数等于逼人再跑五条命令，
        # 那正是本脚本存在的理由。--quiet 只在批处理里用。
        for s, c, m in findings:
            if s == 'ERROR' or not a.quiet:
                print(f'    {s:<7} {c}  {m}')

    print(f'\n合计: {total_e} 个错误，{total_w} 个警告')
    if total_e:
        print('未通过。逐条修完再交付。')
    else:
        print('无阻断错误。警告须逐条处置后才算交付合格——见 references/delivery-contract.md §5。')
    return 1 if total_e else 0


if __name__ == '__main__':
    sys.exit(main())
