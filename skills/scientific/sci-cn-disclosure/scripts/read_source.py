#!/usr/bin/env python3
"""把交底书读成纯文本，`.md` 与 `.docx` 通吃。

写稿阶段源是 Markdown；但稿子发给知产办或代理师之后，回来的是 .docx——那时 docx 才是
最新版本。三个校验器都经此读取，两个方向就都能查。

docx 侧的还原约定（与 render_disclosure.py 互为逆操作）：

- 上下标 run  → `_{...}` / `^{...}`
- 原生 OMML 公式域 → `$$<其中的可见字符>$$`，只用于让校验器知道"此处有一个独立公式"，
  不试图还原 LaTeX（OMML → LaTeX 不是无损的，硬还原只会造出假的源）
- 表格 → 逐行 `| a | b |`
- 标题 → 按 Word 大纲级别加 `#`；无大纲级别时按黑体 + 独占一段推断
"""
from __future__ import annotations

import re
from pathlib import Path

W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


def _para_text(p) -> str:
    """段落纯文本，恢复上下标标记，把 OMML 公式压成 $$...$$ 占位。"""
    out = []
    for child in p._p:
        if child.tag in (f'{M_NS}oMath', f'{M_NS}oMathPara'):
            chars = ''.join(t.text or '' for t in child.iter(f'{M_NS}t'))
            if chars.strip():
                out.append(f'$${chars}$$')
            continue
        if child.tag != f'{W_NS}r':
            continue
        text = ''.join(t.text or '' for t in child.iter(f'{W_NS}t'))
        if not text:
            continue
        va = child.find(f'{W_NS}rPr/{W_NS}vertAlign')
        val = va.get(f'{W_NS}val') if va is not None else None
        if val == 'subscript':
            out.append('_{' + text + '}')
        elif val == 'superscript':
            out.append('^{' + text + '}')
        else:
            out.append(text)
    return ''.join(out).strip()


def _is_heading(p, text: str) -> int:
    """返回标题级别；0 表示正文。"""
    style = (p.style.name or '') if p.style is not None else ''
    m = re.match(r'Heading (\d)', style)
    if m:
        return int(m.group(1))
    outline = p._p.find(f'{W_NS}pPr/{W_NS}outlineLvl')
    if outline is not None:
        return int(outline.get(f'{W_NS}val', '0')) + 1
    # 无大纲级别：黑体 + 短 + 独占一段，按二级标题处理
    runs = [r for r in p.runs if (r.text or '').strip()]
    if runs and len(text) <= 24 and all(r.bold for r in runs):
        return 2
    return 0


def from_docx(path: Path) -> str:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    lines: list[str] = []
    # 按文档流顺序遍历段落与表格，保持二者的相对位置
    for child in doc.element.body.iterchildren():
        if child.tag == f'{W_NS}p':
            p = Paragraph(child, doc)
            text = _para_text(p)
            if not text:
                continue
            lvl = _is_heading(p, text)
            lines.append(('#' * lvl + ' ' + text) if lvl else text)
            lines.append('')
        elif child.tag == f'{W_NS}tbl':
            t = Table(child, doc)
            for ri, row in enumerate(t.rows):
                cells = [' '.join(_para_text(p) for p in c.paragraphs).strip()
                         for c in row.cells]
                lines.append('| ' + ' | '.join(cells) + ' |')
                if ri == 0:
                    lines.append('|' + '---|' * len(cells))
            lines.append('')
    return '\n'.join(lines)


def read_disclosure(path: str | Path) -> str:
    """交底书 → 纯文本。`.docx` 走还原，其余按 UTF-8 文本读取。"""
    p = Path(path)
    if p.suffix.lower() == '.docx':
        return from_docx(p)
    return p.read_text(encoding='utf8')


if __name__ == '__main__':
    import sys
    print(read_disclosure(sys.argv[1]))
