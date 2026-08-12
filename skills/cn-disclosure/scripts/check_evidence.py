#!/usr/bin/env python3
"""权利要求 ↔ 证据台账 的交叉核对。

真正的门禁只有一条:支持状态为 `needs-confirmation` 或 `unsupported` 的技术特征,
绝不能出现在权利要求里。权项中的数值范围,需要"该范围本身"有记载依据,
而不是范围内某个取值有依据。

用法:
    python check_evidence.py 交底书.md evidence.json
    python check_evidence.py 交底书.md evidence.json --json
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
from check_claims import extract_claims  # noqa: E402

SOURCE_ID = re.compile(r'^[PECF]\d{3,}$')
VALID_STATUS = {'explicit', 'inherent', 'needs-confirmation', 'unsupported'}
CLAIMABLE = {'explicit', 'inherent'}


def check(text: str, data: dict) -> list[tuple[str, str, str]]:
    f: list[tuple[str, str, str]] = []

    def add(sev, code, msg):
        f.append((sev, code, msg))

    claims = extract_claims(text)
    claim_numbers = {n for n, _ in claims}
    if not claims:
        add('ERROR', 'NO_CLAIMS', '交底书中未识别到权利要求。')

    # --- source map ---
    source_ids: set[str] = set()
    for rec in data.get('source_map', []):
        sid = str(rec.get('id', ''))
        if not SOURCE_ID.fullmatch(sid):
            add('ERROR', 'SOURCE_ID', f'来源 ID 格式非法：{sid!r}（应为 P/E/C/F + 三位以上数字）。')
        elif sid in source_ids:
            add('ERROR', 'DUPLICATE_SOURCE_ID', f'来源 ID 重复：{sid}。')
        source_ids.add(sid)
        if not str(rec.get('locator', '')).strip():
            add('ERROR', 'SOURCE_LOCATOR', f'{sid} 缺少 locator（应为 file:line 或章节定位）。')
    if not source_ids:
        add('ERROR', 'NO_SOURCE_MAP', 'source_map 为空，无法溯源。')

    # --- evidence ledger ---
    ledger: dict[str, dict] = {}
    for item in data.get('evidence_ledger', []):
        lid = str(item.get('id', ''))
        if not lid:
            add('ERROR', 'LEDGER_ID', '证据台账条目缺少 id。')
            continue
        if lid in ledger:
            add('ERROR', 'DUPLICATE_LEDGER_ID', f'证据台账 id 重复：{lid}。')
        ledger[lid] = item
        status = item.get('support_status')
        if status not in VALID_STATUS:
            add('ERROR', 'SUPPORT_STATUS', f'{lid} 的支持状态非法：{status!r}。')
        if status in CLAIMABLE and not item.get('source_ids'):
            add('ERROR', 'MISSING_SOURCE_LINK', f'{lid} 标为 {status} 但没有来源 ID。')
        for sid in item.get('source_ids', []):
            if sid not in source_ids:
                add('ERROR', 'UNKNOWN_SOURCE_ID', f'{lid} 引用未知来源 ID：{sid}。')
        if not str(item.get('feature', '')).strip():
            add('ERROR', 'EMPTY_FEATURE', f'{lid} 的 feature 为空。')
        # 降级会静默删掉一条本可主张的权项，且第33条不允许事后补回。
        # 因此降级必须留下检索记录，证明是"确无依据"而非"没查全"。
        if status in {'needs-confirmation', 'unsupported'}:
            note = str(item.get('note', '')).strip()
            if len(note) < 20:
                add('WARNING', 'UNDOCUMENTED_DOWNGRADE',
                    f'{lid} 标为 {status} 但未在 note 中记录检索范围。'
                    f'降级前须穷尽：全文（含 Results 与图注）、配置文件、运行产物、消费该值的代码。')
    if not ledger:
        add('ERROR', 'NO_LEDGER', 'evidence_ledger 为空。')

    # --- claim ↔ feature map ---
    mapped: set[int] = set()
    for m in data.get('claim_feature_map', []):
        cn = m.get('claim_number')
        mapped.add(cn)
        if cn not in claim_numbers:
            add('ERROR', 'UNKNOWN_CLAIM', f'特征映射引用不存在的权利要求：{cn}。')
        feat = str(m.get('feature', '')).strip()
        if not feat:
            add('ERROR', 'EMPTY_MAP_FEATURE', f'权利要求 {cn} 的特征映射存在空特征。')
        eids = m.get('evidence_ids', [])
        if not eids:
            add('ERROR', 'UNMAPPED_FEATURE', f'权利要求 {cn} 的特征“{feat[:24]}”没有证据 ID。')
        for eid in eids:
            if eid not in ledger:
                add('ERROR', 'UNKNOWN_EVIDENCE_ID', f'权利要求 {cn} 引用未知证据 ID：{eid}。')
                continue
            st = ledger[eid].get('support_status')
            # 核心门禁
            if st not in CLAIMABLE:
                add('ERROR', 'UNCLAIMABLE_IN_CLAIM',
                    f'权利要求 {cn} 的特征“{feat[:24]}”依赖 {eid}，其支持状态为 {st}，'
                    f'不得写入权利要求（应降入说明书或删除）。')

    for n in sorted(claim_numbers - mapped):
        add('ERROR', 'CLAIM_NOT_MAPPED', f'权利要求 {n} 没有任何特征映射条目。')

    meta = data.get('metadata', {}) or {}

    # --- 目录清点:没看过的地方要写下来 ---
    # "没读某个目录"是个看不见的事实。不落到纸面上，代理师无从判断这份稿子的核实深度，
    # 而漏掉的证据在第 33 条之下再也补不回来。
    inv = meta.get('inventory')
    if not inv:
        add('WARNING', 'NO_INVENTORY',
            'metadata.inventory 为空。阶段 1 须先清点工作目录，再逐个目录表态'
            '（读了 / 与本发明无关 / 打不开）。清单只能确认想到的东西，发现不了没想到的。')
    elif isinstance(inv, dict):
        blank = [k for k, v in inv.items() if not str(v).strip()]
        if blank:
            add('WARNING', 'INVENTORY_UNDECIDED',
                f'有 {len(blank)} 个目录清点后未表态：{blank[:5]}。')

    # --- 在先申请:全流程第一件事 ---
    # 同一发明若已有在先申请，后面所有工作的前提都变了。八次实测运行里只有一次想到去查，
    # 而那次查出来确有一件已授权的在先专利——其余七次都在为一个已拿到专利的方案重写交底书。
    # 这个信息读多少遍材料都不会出现，只有主动检索才有，所以必须单独把关。
    pf = meta.get('prior_filings')
    if pf is None:
        add('WARNING', 'NO_PRIOR_FILING_CHECK',
            'metadata.prior_filings 缺失。阶段 0 须先检索同一发明有无在先申请'
            '（按发明人姓名、申请人机构、技术主题三路检索）。'
            '找到的记公开号/授权公告号与权利要求 1 主题；未找到的记检索式与检索库。')
    elif isinstance(pf, dict) and not str(pf.get('searched', '')).strip():
        add('WARNING', 'PRIOR_FILING_NO_TRACE',
            'metadata.prior_filings 未记录检索式与检索库——"没找到"和"没查过"'
            '在纸面上必须能分开。')
    elif isinstance(pf, list) and pf:
        add('WARNING', 'PRIOR_FILING_FOUND',
            f'检索到 {len(pf)} 件在先申请。交付前须与代理师核对其权利要求的覆盖范围，'
            f'再决定本交底书的保护范围如何避让或衔接。')

    # --- 对不上的地方，必须带着它的问题 ---
    # 证据强度序位只能给出"暂时用哪个"，给不出"哪个是对的"——同级证据内部打架时
    # (论文正文 vs 论文表格、配置 A vs 配置 B)序位直接失效。第 33 条之下猜错补不回来，
    # 所以每一处不一致都必须落成一条问发明人的技术事实题，而不是起草者自行拍板。
    disc = meta.get('discrepancies')
    if isinstance(disc, list):
        mute = [d for d in disc
                if isinstance(d, dict) and not str(d.get('question', '')).strip()]
        if mute:
            add('WARNING', 'DISCREPANCY_NO_QUESTION',
                f'有 {len(mute)} 处不一致没有写 question 字段。序位取的值只是临时占位，'
                f'不是结论——每处都要写明「A 处记 X、B 处记 Y，实际以哪个为准」并问发明人。')
        if disc:
            add('WARNING', 'DISCREPANCY_PENDING',
                f'记录了 {len(disc)} 处载体之间对不上的地方，交付前须与发明人逐条定夺以哪个为准。')

    # --- 主文档逐节表态 ---
    # 材料一多，"通读全文"就会被挤薄，而且挤薄了没有任何迹象:同一篇论文里的自相矛盾，
    # 只给论文时被发现，加上几十兆源码之后同一处就漏掉了。所以这一项要独立于材料量把关。
    cov = meta.get('source_coverage')
    if not cov:
        add('WARNING', 'NO_SOURCE_COVERAGE',
            'metadata.source_coverage 为空。主文档的每一节都要么在 source_map 里有 ID，'
            '要么在此写明「与本发明无关」——否则读没读全，事后看不出来。')
    elif isinstance(cov, dict):
        blank = [k for k, v in cov.items() if not str(v).strip()]
        if blank:
            add('WARNING', 'COVERAGE_UNDECIDED',
                f'有 {len(blank)} 节列出但未表态：{blank[:5]}。')

    # --- 自由深读:有源码就该有 ---
    # 定向核实只能确认已经在问的问题。实现缺陷长在没人想到要问的地方，
    # 只有把代码当代码通读才会撞见——这一步不显式留出来，就不会发生。
    has_code = any(str(r.get('id', '')).startswith('C') for r in data.get('source_map', []))
    if has_code and 'anomalies' not in meta:
        add('WARNING', 'NO_ANOMALY_PASS',
            'source_map 里有代码来源（C 前缀）却没有 metadata.anomalies。'
            '阶段 1 的自由深读须单独做一遍并留痕；确无反常时写成空数组。')

    # --- 待确认项:能问就该问，没问就该记 ---
    q = data.get('inventor_questions')
    if q is None:
        add('WARNING', 'NO_QUESTIONS_KEY',
            'evidence.json 缺少 inventor_questions 数组。该问发明人而当下无人可答的问题'
            '必须记在这里，否则会随本次运行一起消失。确无待确认项时写成空数组。')
    elif q:
        add('WARNING', 'PENDING_INVENTOR_QUESTIONS',
            f'有 {len(q)} 条待确认项尚未解决，交付前须与发明人逐条过。')

    # --- numeric ranges in claims need a range-level basis ---
    rng = re.compile(r'(\d+(?:\.\d+)?)\s*(?:至|到|~|—|-)\s*(\d+(?:\.\d+)?)')
    bases = ' '.join(str(i.get('feature', '')) + str(i.get('note', ''))
                     for i in data.get('evidence_ledger', []))
    for n, body in claims:
        compact = re.sub(r'\s+', '', body)
        for m in rng.finditer(compact):
            lo, hi = m.groups()
            # "权利要求1至13" 是引用，不是数值范围
            if '权利要求' in compact[max(0, m.start() - 5):m.start()]:
                continue
            if f'{lo}' not in bases or f'{hi}' not in bases:
                add('WARNING', 'RANGE_BASIS',
                    f'权利要求 {n} 含数值范围 {lo}–{hi}；确认台账中记录了该"范围"本身的依据，'
                    f'而非仅记录了范围内的某个取值。')
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description='权利要求 ↔ 证据台账 交叉核对')
    ap.add_argument('disclosure')
    ap.add_argument('evidence')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    text = read_disclosure(a.disclosure)
    data = json.loads(Path(a.evidence).read_text(encoding='utf8'))
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
            print('PASS: 每条权利要求特征均有可主张的证据支撑。')
    return 1 if any(s == 'ERROR' for s, *_ in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
