# 交付契约

交付前必须全部成立。**这里是唯一的合格判据**——各阶段的「门禁」只说该跑哪条命令,判据在本文件。

## 1. 交付物

| 文件 | 要求 |
|---|---|
| `交底书.md` | 人类可编辑的源 |
| `交底书.docx` | 公式为原生 OMML、附图已内嵌 |
| `evidence.json` | `source_map` / `evidence_ledger` / `claim_feature_map` 三者非空;`metadata` 下 `prior_filings`(在先申请检索)、`inventory`(目录清点)、`source_coverage`(主文档逐节表态)、`discrepancies`(每条带 `question`)、`inventor_questions` 齐备,有源码时另加 `anomalies`(自由深读所见) |
| `alternatives.json` | 每个具体选择均已处置 |
| `figures/fig*.png` | 与 `figures/specs/*.json` 一一对应 |

由 `check_complete.py`(文件与硬性键)与 `check_evidence.py`(`metadata.inventory`、`inventor_questions`)共同核对。

## 2. 可追溯性

- 权利要求里每一条实质特征,至少映射到一个证据 ID
- 每个证据 ID 在 `source_map` 里有 `file:line` 或章节定位
- 权利要求里每一个数值,在 `alternatives.json` 里有处置:标 `essential`,或给出替代方案与依据
- 附图里每个标记,在正文以「名称 + 编号」的形式出现过
- 台账所记的证据级别**不高于实际所据**(实测 > 代码 > 论文 > 口述)

## 3. 不得写入权利要求

- `support_status` 为 `needs-confirmation` 或 `unsupported` 的特征
- 没有「范围本身」依据的数值范围——范围内某个取值有依据不算
- `[待确认:…]` `[待检索:…]` 这类占位标记

## 4. 不得出现在交底书正文

- 证据 ID、支持状态、起草注记、校验器输出
- `status` 为 `speculative` 的替代方案
- 未经打开核实的专利号、文献、URL
- 末端落在「设计结果」「技术结果」「处理结果」这类空话上的独立权利要求

## 5. 校验门禁

```bash
python scripts/check_all.py 交底书.md
```

**任一 ERROR 不得交付。** WARNING 逐条看过并处置:采纳的改,不采纳的在对应台账条目的 `note` 里写明理由。

## 6. 达不到时怎么办

**不要为了让校验器变绿而删内容。** 缺的是事实就回去查;查不到就留白,记进 `QUESTIONS`,把缺口交给代理师。

**标着缺口的稿子可以交付,假装没有缺口的不行。**
