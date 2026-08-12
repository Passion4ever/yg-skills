# sci-cn-disclosure

把论文、源码、运行产物、附图、发明人笔记,转成**中国发明专利技术交底书**,交学校知识产权办公室与专利代理所。

一句话概括它的价值:**交底书里的每一句话都能指回出处**——权项特征溯源到论文行号与代码行号,每个可替代实施方式都有举证等级,每一处"论文和代码对不上"都落到纸面上并附一条问发明人的问题。

## 它不做什么

- **不产出可直接递交国知局的四件套**(权利要求书 / 说明书 / 说明书附图 / 说明书摘要)——那是代理师的活
- **不做查新,不给可专利性结论**——只为背景技术做定向检索,并在动笔前查一次"这个发明有没有被申请过"
- **不能保证出处本身没被读错**——校验器只能验"台账 ↔ 文档"一致,验不了"台账 ↔ 事实"

## 安装

复制到个人技能目录即可:

```bash
git clone <this-repo> ~/.claude/skills/sci-cn-disclosure
```

## 依赖

六个 `check_*.py` **全是纯标准库**,校验 Markdown 时任何 Python 都能直接跑。只有下面几种情形要装包:

| 做什么 | 需要 |
|---|---|
| 校验 `.md` | 无 |
| 校验 `.docx`(代理师回稿) | `python-docx` |
| 出稿 `render_disclosure.py` | `python-docx` `latex2mathml` `Pillow` |
| 画图 `render_figures.py` | `cairosvg` `Pillow` + **系统装中文字体** |

中文字体是硬要求,缺了渲出来是一片空心方框。开工前先自检:

```bash
python scripts/render_figures.py --check-env
```

## 用法

直接说「帮我写份技术交底书,材料在 xxx 目录」即可。技能会走完八个阶段,每个阶段有固定的**产物**与**门禁**:

| 阶段 | 产物 |
|---|---|
| 0 信息采集 | 表头 + 公开状态 + **在先申请检索** |
| 1 源材料映射与核实 | 目录清点、逐节表态、载体核对、自由深读 |
| 2 证据台账 | `evidence.json` 的 `evidence_ledger` |
| 3 权利要求 | 必要特征链 / 优选细化的划分 |
| 4 说明书 | 五节 + 效果表 + **首轮实质评审** |
| 5 可替代实施方式 | `alternatives.json`,四态举证 |
| 6 附图 | spec → SVG/PNG,附图标记锚定正文 |
| 7 出稿与评审 | docx(公式为原生 OMML)+ 收尾复核 |

交付前跑一次全套:

```bash
python scripts/check_all.py 交底书.md
```

**任一 ERROR 不得交付。WARNING 不阻断,但每条都要过一遍**——零错误不等于可以交,合格判据见 `references/delivery-contract.md`。

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
  └ vendor/figure_renderer.py         基础渲染器（随技能分发，勿改）
scripts/render_disclosure.py          Markdown → docx（公式为原生 OMML）
scripts/read_source.py                .md / .docx 统一读取
scripts/math_to_omml.py               LaTeX → Word 公式域
```

`references/` 下五份按需加载,走到对应阶段才读。

## 成熟度

跑过两轮 A/B 对照,共 8 次运行,跨两个领域(蓝藻启动子识别 / 蛋白口袋分子生成):

**已验证:** 交付物齐全 4/4;所引 7 个专利号逐一核过数据库,名称、申请人、申请日、公开日全部正确,**零编造**;换领域零素材泄漏;自由深读 2/2 触发。

**未验证:** 在先申请检索、载体核对框架、效果表写作规则是最后一轮评测之后写的,**只做过合成测试**;八次运行全为无人值守,"停下来问用户"这条主路径未被走过;测试材料集中在算法与生物领域,机械 / 化工类只在纸面上适配过。

## 第三方代码

| 文件 | 来源 | 许可 |
|---|---|---|
| `scripts/vendor/figure_renderer.py` | ARIS 项目的 FigureSpec 渲染器 | MIT © 2026 wanshuiyin |
| `scripts/math_to_omml.py` | nature-skills / nature-paper-to-patent | Apache-2.0 |

两者均按原样使用。更新方式:用上游文件覆盖,并保留文件头的来源说明;`figure_renderer.py` 也可用环境变量 `CN_DISCLOSURE_RENDERER` 指向别处。
