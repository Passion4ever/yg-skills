#!/usr/bin/env python3
"""把附图 spec 渲染为 SVG 与 PNG。

在 figure-spec 的基础渲染器之上补四件它没有的能力:

  - 中文字体绑定:见下方 `resolve_cjk_font`。**不做这件事就会渲出一片空心方框。**
  - 下标与上标:spec 里写 `_{...}` / `^{...}`，此处转为偏移 tspan。**这是必须的**——
    直接写 `t_next` 会原样渲染成带下划线的字面文本，看上去像没排版的源码。
  - 分组标签加深:基础渲染器写死 #999999，印刷偏淡。
  - 正交反馈回路:spec 中非 schema 的 "feedback" 键，形如
    [{from_xy, to_xy, channel_x, label}]。中心到中心的直线无法绕开中间的方框。

用法:
    python render_figures.py --specs <spec目录> --out <输出目录> [fig1 fig2 ...]
    python render_figures.py --check-env          # 只自检渲染器与中文字体
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# 基础渲染器随技能一起分发(scripts/vendor/)。曾经写死为另一个项目里的绝对路径,
# 换台机器就整个阶段 6 崩掉。
RENDERER_ENV = 'CN_DISCLOSURE_RENDERER'
FONT_ENV = 'CN_DISCLOSURE_CJK_FONT'

# 两个字形不同的汉字。tofu 的判据是"不同的字渲成同一个方框"，一个字测不出来。
CJK_PROBE = ('蓝', '藻')

# 覆盖面与字重都靠谱的在前。列表是偏好序，不是白名单——都没有时取 fc-list 的第一个。
FONT_PREFERENCE = (
    'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Source Han Sans SC', 'Source Han Sans CN',
    'Noto Serif CJK SC', 'Source Han Serif SC', 'WenQuanYi Zen Hei',
    'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', 'PingFang SC',
    'Heiti SC', 'Droid Sans Fallback',
)

ARROW = '''<defs><marker id="arrow-fb" markerWidth="9" markerHeight="9" refX="8" refY="3"
 orient="auto" markerUnits="strokeWidth"><polygon points="0,0 9,3 0,6" fill="#000000"/></marker></defs>'''

# Sub/superscripts are written _{...} / ^{...} in the specs and turned into shifted
# tspans here. SVG baseline-shift is ignored by cairosvg, so shift with dy and track
# the cumulative offset so every chunk lands on its intended baseline.
SCRIPT_RE = re.compile(r'([_^])\{([^{}]*)\}')
TEXT_RE = re.compile(r'(<text\b[^>]*>)(.*?)(</text>)', re.S)
FONT_ATTR_RE = re.compile(r'font-family="([^"]*)"')
FONT_CSS_RE = re.compile(r'font-family\s*:\s*([^;"}]*)')


def die(msg: str) -> None:
    sys.exit(f'render_figures: {msg}')


def resolve_renderer() -> Path:
    """基础渲染器的位置。环境变量 > 随技能分发的 vendor 副本。"""
    env = os.environ.get(RENDERER_ENV)
    if env:
        p = Path(env).expanduser()
        if not p.is_file():
            die(f'{RENDERER_ENV} 指向的文件不存在:{p}')
        return p
    p = Path(__file__).resolve().parent / 'vendor' / 'figure_renderer.py'
    if not p.is_file():
        die(f'找不到基础渲染器:{p}\n'
            f'  从 figure-spec 技能的 tools/figure_renderer.py 复制一份到该位置，\n'
            f'  或设 {RENDERER_ENV}=<路径>。')
    return p


def _fc(args: list[str]) -> list[str]:
    try:
        r = subprocess.run(['fc-list', *args], capture_output=True, text=True, timeout=20)
    except (FileNotFoundError, subprocess.SubprocessError):
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def _fc_match_file(family: str) -> str:
    """fontconfig 拿到这个族名之后，实际会给出哪个文件。"""
    try:
        r = subprocess.run(['fc-match', family, '--format', '%{file}'],
                           capture_output=True, text=True, timeout=20)
    except (FileNotFoundError, subprocess.SubprocessError):
        return ''
    return r.stdout.strip()


def _has_glyphs(font_file: str) -> bool:
    """字体文件里这两个汉字是不是真有字形(而不是同一个 .notdef 方框)。

    判据是把两个字形不同的汉字各画一遍再比位图:缺字时字体给的是同一个 .notdef,
    两张图会完全相同。只画一个字判不出来——.notdef 本身也是有墨的。

    查不成时返回 True 放行，但**必须出声**:之前这里静默 return True，
    Pillow 换版本后 API 变了，探测器整整失效而没有任何迹象。
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('render_figures: 无 Pillow，跳过字形自检(装上可自动拦截豆腐块)', file=sys.stderr)
        return True
    try:
        f = ImageFont.truetype(font_file, 32)
        bitmaps = []
        for ch in CJK_PROBE:
            im = Image.new('L', (48, 48), 0)
            ImageDraw.Draw(im).text((4, 4), ch, font=f, fill=255)
            bitmaps.append(im.tobytes())
    except Exception as e:
        print(f'render_figures: 字形自检跑不起来({type(e).__name__}: {e})，'
              f'跳过——请人工确认 PNG 里的汉字没变成空心方框', file=sys.stderr)
        return True
    if not any(bitmaps[0]):              # 一片空白 = 根本没画出来
        return False
    return bitmaps[0] != bitmaps[1]      # 两个字长得一模一样 = tofu


def resolve_cjk_font() -> str:
    """挑一个 cairo 拿得到、且真有汉字字形的族名。

    cairosvg 走 cairo 的 toy font API，**不做逐字形回退**:font-family 列表里第一个
    匹配上的族拿不出这个字，它就画 .notdef 方框，不会去试下一个族。所以中文字体必须
    显式排在最前，"系统里装了"是不够的。
    """
    env = os.environ.get(FONT_ENV)
    if env:
        return env

    # 一个族名对应多个字重文件，所以存集合:回环校验只要 fc-match 落在其中之一即可，
    # 比对"第一个见到的文件"会因为撞上另一个字重而误判。
    installed: dict[str, set[str]] = {}
    for ln in _fc([':lang=zh', '--format', '%{file}\t%{family}\n']):
        file, _, fams = ln.partition('\t')
        for fam in fams.split(','):
            installed.setdefault(fam.strip(), set()).add(file.strip())
    if not installed:
        die('系统里没有中文字体，渲出来会是一片空心方框。\n'
            '  Debian/Ubuntu: sudo apt install fonts-noto-cjk\n'
            '  RHEL/CentOS:   sudo dnf install google-noto-sans-cjk-fonts\n'
            '  conda:         conda install -c conda-forge fonts-anaconda\n'
            f'  已装但未被 fontconfig 收录时，用 {FONT_ENV}=<族名> 直接指定。')

    order = [f for f in FONT_PREFERENCE if f in installed] + sorted(installed)
    for fam in order:
        matched = _fc_match_file(fam)
        # 族名要能被 fontconfig 解析回同一个文件，否则 cairo 拿到的是别的字体
        if matched and matched in installed[fam] and _has_glyphs(matched):
            return fam
    die(f'系统里有 {len(installed)} 个中文字体，但没有一个能通过字形自检。\n'
        f'  候选:{", ".join(order[:5])}\n'
        f'  用 {FONT_ENV}=<族名> 手动指定，或重装 fonts-noto-cjk。')


def apply_font(svg: str, family: str) -> str:
    """把中文族名插到每处 font-family 的最前面。"""
    # 族名带空格必须引起来，且只能用单引号——外层 SVG 属性已经占用了双引号。
    quoted = f"'{family}'"

    def head(existing: str) -> str:
        rest = [q for q in (x.strip() for x in existing.split(','))
                if q and q.strip('\'"') != family]
        return ', '.join([quoted] + rest)
    svg = FONT_ATTR_RE.sub(lambda m: f'font-family="{head(m.group(1))}"', svg)
    svg = FONT_CSS_RE.sub(lambda m: f'font-family:{head(m.group(1))}', svg)
    return svg


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _typeset(content, base_fs):
    if '_{' not in content and '^{' not in content:
        return content
    d = round(base_fs * 0.30, 1)
    cur, out, pos = 0.0, [], 0

    def chunk(text, target, small=False):
        nonlocal cur
        if text == '' and target == cur:
            return
        attrs = ''
        if target != cur:
            attrs += f' dy="{round(target - cur, 1)}"'
            cur = target
        if small:
            attrs += ' font-size="0.72em"'
        out.append(f'<tspan{attrs}>{_esc(text)}</tspan>')

    for m in SCRIPT_RE.finditer(content):
        chunk(content[pos:m.start()], 0)
        chunk(m.group(2), d if m.group(1) == '_' else -d, small=True)
        pos = m.end()
    chunk(content[pos:], 0)
    return ''.join(out)


def _width(text, fs, scale=1.0):
    # Same heuristic the renderer uses to size boxes, so the two stay consistent.
    return sum(fs * (1.0 if ord(c) > 0x2E80 else 0.6) for c in text) * scale


def _plain_width(content, fs):
    """Rendered width once _{} / ^{} markers become shifted 0.72em tspans."""
    w, pos = 0.0, 0
    for m in SCRIPT_RE.finditer(content):
        w += _width(content[pos:m.start()], fs)
        w += _width(m.group(2), fs, 0.72)
        pos = m.end()
    return w + _width(content[pos:], fs)


def typeset_svg(svg):
    """cairosvg mis-flows tspans under text-anchor="middle", so centred text that
    carries scripts is re-anchored to "start" at an explicitly computed left edge."""
    def repl(m):
        open_tag, body, close = m.groups()
        if '<tspan' in body or ('_{' not in body and '^{' not in body):
            return m.group(0)
        fs = float(re.search(r'font-size="([\d.]+)"', open_tag).group(1)) \
            if re.search(r'font-size="([\d.]+)"', open_tag) else 14.0
        tag = open_tag
        if 'text-anchor="middle"' in tag:
            cx = float(re.search(r'\bx="([-\d.]+)"', tag).group(1))
            left = cx - _plain_width(body, fs) / 2
            tag = tag.replace('text-anchor="middle"', 'text-anchor="start"')
            tag = re.sub(r'\bx="[-\d.]+"', f'x="{left:.1f}"', tag)
        return tag + _typeset(body, fs) + close
    return TEXT_RE.sub(repl, svg)


def feedback_svg(loops):
    out = [ARROW]
    for lp in loops:
        (fx, fy), (tx, ty) = lp['from_xy'], lp['to_xy']
        if 'channel_y' in lp:          # vertical channel: down/up, across, then in
            cy = lp['channel_y']
            d = f"M {fx},{fy} L {fx},{cy} L {tx},{cy} L {tx},{ty}"
            default_label_xy = [(fx + tx) / 2, cy - 6]
        else:
            cx = lp['channel_x']
            d = f"M {fx},{fy} L {cx},{fy} L {cx},{ty} L {tx},{ty}"
            default_label_xy = [cx - 6, (fy + ty) / 2]
        dash = ' stroke-dasharray="6,4"' if lp.get('style') == 'dashed' else ''
        out.append(f'<path d="{d}" fill="none" stroke="#000000" stroke-width="2"{dash} '
                   f'marker-end="url(#arrow-fb)"/>')
        if lp.get('label'):
            lx, ly = lp.get('label_xy', default_label_xy)
            anchor = lp.get('label_anchor', 'end')
            out.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="13" '
                       f'fill="#000000" text-anchor="{anchor}">{lp["label"]}</text>')
    return '\n'.join(out)


def build(spec_path: Path, out_dir: Path, renderer: Path, font: str) -> Path:
    spec = json.loads(spec_path.read_text(encoding='utf8'))
    loops = spec.pop('feedback', [])

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / spec_path.name
        tmp.write_text(json.dumps(spec, ensure_ascii=False), encoding='utf8')
        out_dir.mkdir(parents=True, exist_ok=True)
        svg_path = out_dir / f'{spec_path.stem}.svg'
        r = subprocess.run([sys.executable, str(renderer), 'render', str(tmp),
                            '--output', str(svg_path)], capture_output=True, text=True)
        if r.returncode != 0:
            die(f'{spec_path.name} 渲染失败:\n{(r.stderr or r.stdout).strip()}')

    svg = svg_path.read_text(encoding='utf8')
    svg = svg.replace('fill="#999999" font-weight="bold"', 'fill="#333333" font-weight="bold"')
    svg = re.sub(r'(fill="#999999")(?=[^>]*font-weight="bold")', 'fill="#333333"', svg)
    if loops:
        svg = svg.replace('</svg>', feedback_svg(loops) + '\n</svg>')
    svg = typeset_svg(svg)
    svg = apply_font(svg, font)
    svg_path.write_text(svg, encoding='utf8')

    try:
        import cairosvg
    except ImportError:
        die('缺少 cairosvg,无法出 PNG。pip install cairosvg')
    png = out_dir / f'{spec_path.stem}.png'
    cairosvg.svg2png(url=str(svg_path), write_to=str(png), scale=1.3)
    return svg_path


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description='附图 spec → SVG + PNG')
    ap.add_argument('--specs', default='figures/specs', help='spec 目录')
    ap.add_argument('--out', default='figures', help='输出目录')
    ap.add_argument('--font', help=f'中文族名，覆盖自动挑选(同 {FONT_ENV})')
    ap.add_argument('--check-env', action='store_true', help='只自检渲染器与中文字体')
    ap.add_argument('names', nargs='*', help='图名主干，省略则全部')
    a = ap.parse_args()

    renderer = resolve_renderer()
    font = a.font or resolve_cjk_font()
    print(f'渲染器: {renderer}\n中文字体: {font}')
    if a.check_env:
        return 0

    specs, out = Path(a.specs), Path(a.out)
    names = a.names or [p.stem for p in sorted(specs.glob('fig*.json'))]
    if not names:
        die(f'{specs} 下没有 fig*.json')
    for n in names:
        print('built', build(specs / f'{n}.json', out, renderer, font))
    print('\n渲染完必须逐张打开看过——压字、穿线、截断、缩放、字形，校验器都查不出来。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
