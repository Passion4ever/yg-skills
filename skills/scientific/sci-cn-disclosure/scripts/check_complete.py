#!/usr/bin/env python3
"""交付完整性检查:交付物是否齐全（对照 references/delivery-contract.md §1）。

阶段可以被静默跳过——已经发生过一次:附图说明写了三幅图、一张实际的图都没有,直到
被人问起才发现。其余校验器各查各的局部,没有任何一个会说"你少走了一个阶段"。

此脚本只查"该有的东西在不在",不判断内容好坏。

用法:
    python check_complete.py 交底书.md
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

# 说明书法定五部分，缺一即为结构不完整
SPEC_PARTS = ['技术领域', '背景技术', '发明内容', '附图说明', '具体实施方式']
# evidence.json 的硬性键:缺了根本无法溯源，报 ERROR。
# 另两个键 metadata.inventory 与 inventor_questions 由 check_evidence.py 以警告把关
# ——它们缺失不阻断校验，但交付前必须补齐。两处合起来才是契约 §1 的全部。
REQUIRED_EVIDENCE_KEYS = ['source_map', 'evidence_ledger', 'claim_feature_map']


def check(src: Path) -> list[tuple[str, str, str]]:
    f: list[tuple[str, str, str]] = []

    def add(sev, code, msg):
        f.append((sev, code, msg))

    d = src.parent
    text = read_disclosure(src)

    # 阶段 0：表头
    for field in ['申请人', '发明人', '技术联系人']:
        if field not in text[:1200]:
            add('ERROR', 'HEADER_INCOMPLETE', f'表头缺少「{field}」。')
    if '公开充分' not in text[:2000] and '核准' not in text[:2000]:
        add('WARNING', 'NO_SUFFICIENCY_DECL', '表头未见须发明人核准的公开充分性声明。')

    # 阶段 2：证据台账
    ev = d / 'evidence.json'
    if not ev.exists():
        add('ERROR', 'NO_EVIDENCE_LEDGER', 'evidence.json 不存在——阶段 2 未完成。')
    else:
        j = json.loads(ev.read_text(encoding='utf8'))
        for k in REQUIRED_EVIDENCE_KEYS:
            if not j.get(k):
                add('ERROR', 'EVIDENCE_INCOMPLETE', f'evidence.json 缺少或清空了 {k}。')

    # 阶段 3：权利要求
    if not re.search(r'(?m)^#*\s*权利要求书\s*$', text):
        add('ERROR', 'NO_CLAIMS_SECTION', '未找到「权利要求书」一节。')

    # 阶段 4：说明书五部分
    for part in SPEC_PARTS:
        if not re.search(rf'(?m)^#*\s*{part}\s*$', text):
            add('ERROR', 'SPEC_PART_MISSING', f'说明书缺少法定部分「{part}」。')
    if '|' not in text:
        add('WARNING', 'NO_EFFECT_TABLE', '未见任何表格——效果对比表是否遗漏？')

    # 阶段 5：可替代实施方式
    alt = d / 'alternatives.json'
    if not alt.exists():
        add('ERROR', 'NO_ALT_LEDGER', 'alternatives.json 不存在——阶段 5 未完成。')
    if not re.search(r'(?m)^#*\s*\**\s*可替代实施方式', text):
        add('ERROR', 'NO_ALT_SECTION', '正文缺少「可替代实施方式」一节。')

    # 阶段 6：附图
    imgs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)
    if not imgs:
        add('ERROR', 'NO_FIGURES', '未插入任何附图——阶段 6 未完成。')
    else:
        for i in imgs:
            if not (d / i).exists():
                add('ERROR', 'FIGURE_MISSING', f'附图文件不存在：{i}。')
        if not (d / 'figures' / 'specs').exists():
            add('WARNING', 'NO_FIGURE_SPECS', '未见 figures/specs——附图 spec 是否未随稿保存？')

    # 阶段 7：出稿
    if not src.with_suffix('.docx').exists():
        add('WARNING', 'NO_DOCX', f'未见 {src.stem}.docx——阶段 7 是否未出稿？')

    # 待确认项
    todo = re.findall(r'[\[【](?:TO CONFIRM|待确认)[^\]】]*[\]】]', text)
    if todo:
        add('WARNING', 'PENDING_CONFIRMATION',
            f'正文仍含 {len(todo)} 处待确认标记，交付前须与发明人逐条确认。')
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description='交付完整性检查')
    ap.add_argument('disclosure')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    findings = check(Path(a.disclosure))
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
            print('PASS: 交付物齐全。')
    return 1 if any(s == 'ERROR' for s, *_ in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
