# sci-cn-disclosure

把论文、源码、运行产物、附图、发明人笔记，转成**中国发明专利技术交底书**，交学校知识产权办公室与专利代理所。

## 它不做什么

- **不产出可直接递交国知局的四件套**（权利要求书 / 说明书 / 说明书附图 / 说明书摘要）——那是代理师的活
- **不做查新，不给可专利性结论**——只为背景技术做定向检索，并在动笔前查一次「这个发明有没有被申请过」
- **不能保证出处本身没被读错**——校验器只能验「台账 ↔ 文档」一致，验不了「台账 ↔ 事实」

## 依赖

六个 `check_*.py` 全是纯标准库，校验 Markdown 不必配环境。

| 做什么 | 需要 |
|---|---|
| 校验 `.md` | 无 |
| 校验 `.docx`（代理师回稿） | `python-docx` |
| 出稿 `render_disclosure.py` | `python-docx` `latex2mathml` `Pillow` |
| 画图 `render_figures.py` | `cairosvg` `Pillow` + **系统装中文字体** |

中文字体是硬要求，缺了渲出来是一片空心方框。开工前先自检：

```bash
python scripts/render_figures.py --check-env
```

## 用法

直接说「帮我写份技术交底书，材料在 xxx 目录」即可。技能会走完八个阶段，每个阶段有固定的**产物**与**门禁**：

| 阶段 | 产物 |
|---|---|
| 0 信息采集 | 表头 + 公开状态 + **在先申请检索** |
| 1 源材料映射与核实 | 目录清点、逐节表态、载体核对、自由深读 |
| 2 证据台账 | `evidence.json` 的 `evidence_ledger` |
| 3 权利要求 | 必要特征链 / 优选细化的划分 |
| 4 说明书 | 五节 + 效果表 + **首轮实质评审** |
| 5 可替代实施方式 | `alternatives.json`，四态举证 |
| 6 附图 | spec → SVG/PNG，附图标记锚定正文 |
| 7 出稿与评审 | docx（公式为原生 OMML）+ 收尾复核 |

交付前跑一次全套：

```bash
python scripts/check_all.py 交底书.md
```

**任一 ERROR 不得交付。WARNING 不阻断，但每条都要过一遍**——零错误不等于可以交，合格判据见 `references/delivery-contract.md`。

## 目录

```
SKILL.md                              常驻上下文 —— 流程与判断标准

references/delivery-contract.md       交付前逐条核对 —— 唯一的合格判据
references/template-disclosure.md     写说明书时读 —— 只管形式，不管判断
references/alternatives-discipline.md 写可替代实施方式时读 —— 举证纪律
references/figure-standards.md        画附图时读 —— 该画哪几张、验收标准
references/examiner-review.md         外部评审时读 —— 提示词模板与已知失误模式

scripts/check_all.py                  【入口】一条命令跑完下面五个
  ├ check_complete.py                 交付物是否齐全
  ├ check_claims.py                   权项结构
  ├ check_evidence.py                 权项特征 ↔ 证据台账
  ├ check_alternatives.py             具体选择枚举 ↔ 替代方案台账
  └ check_figures.py                  附图编号、附图标记 ↔ 正文

scripts/render_figures.py             附图 spec → SVG + PNG
  └ vendor/figure_renderer.py         基础渲染器
scripts/render_disclosure.py          Markdown → docx（公式为原生 OMML）
scripts/read_source.py                .md / .docx 统一读取
scripts/math_to_omml.py               LaTeX → Word 公式域
```
