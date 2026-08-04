# Evidence ledger — SiamProm

访问日期统一为 2026-08-04。标签含义：`[论文]` 论文或补充材料明示；`[代码]` 官方仓库、配置或数据直接显示；`[外部核验]` 第一方外部文献支持或挑战；`[推断]` 基于已列材料的可复查分析；`[缺失]` 应有信息未公开；`[冲突]` 论文、补充、代码或数据不一致。

| evidence ID | 标签 | 来源 | 版本/commit | locator | supported statement | access status |
|---|---|---|---|---|---|---|
| E01 | [论文] | Yang et al., *Briefings in Bioinformatics* | 25(3), bbae193, DOI 10.1093/bib/bbae193 | [OUP article](https://academic.oup.com/bib/article/25/3/bbae193/7663433)，title/abstract/article history | 论文身份、作者、正式发表日期与核心自述贡献。 | 可访问；正式全文与 PDF 已获取 |
| E02 | [论文] | 主文 | 正式发表版 | Materials and Methods, “Promoter collection”; PDF p.2 | 论文称从文献 [20] 收集 13,705 条 experimentally validated promoter，截取 −60…+20，经 CD-HIT-EST 0.8 得到 12,566 条。 | 可访问 |
| E03 | [论文] | 补充材料 | `supplementary_information_bbae193.docx` | “Sampling of pseudo-promoters” | 34 条所谓 IND 实际从 PCC 7120 CDS 中按 `WAWWWTNNNNNYR` 搜索并截取，负标签依据是不在实验 promoter 集合。 | 可访问；原始核查材料已保存 |
| E04 | [论文] | 主文 | 正式发表版 | “Non-promoter construction”, Figure 1 | phantom 声称固定 −12…−7 Pribnow box 与 −1…0 TSS，余段分 10 份、随机化 7 份，并将 GC 差约束为 <5%。 | 可访问 |
| E05 | [冲突] | 官方仓库 `data/full_phantom_data.fasta` 的逐对核查 | `6b34869a1104a42acd215d5e4b47a720b357eb10` | 12,566 对按 header 配对；比较索引 48–53、59–60、每条 GC% | 所有对只完整固定索引 48–53；仅 980 对同时保留声称的 TSS 两位；3,825 对最终 GC 百分点差 ≥5，最大 23.457。公开成品与算法描述冲突。 | 可访问并复核；官方数据无本地改动 |
| E06 | [缺失] | 官方 GitHub 仓库 | `6b34869a1104a42acd215d5e4b47a720b357eb10` | [repository](https://github.com/Passion4ever/SiamProm)，根目录与 `data/` 全文件清单 | 仓库提供四套成品 FASTA，但没有 random/CDS/partial/phantom 生成脚本，也没有 motif 分析脚本。 | 仓库可访问；所需脚本缺失 |
| E07 | [论文] | 主文与补充材料 | 正式发表版 | 主文 “Datasets”; supplement “Parameter setting” | 四套平衡数据各含 12,566 正/负例、81 bp，并报告 10-fold cross-validation；补充给出 Optuna、早停和主要超参数。 | 可访问 |
| E08 | [冲突] | `srcs/data_loader.py`, `conf/data/train_data.yaml`, `train.py` | `6b34869a1104a42acd215d5e4b47a720b357eb10` | `data_loader.py:40–65`; config `val_size: 0.1`; `train.py:52–54` | 公开入口用 `random_split` 做一次 90/10 train/validation，无 KFold/test；且按单条序列而非模板—派生对分组。与 10 折报告冲突。 | 可访问；代码路径可执行但未跑完整训练 |
| E09 | [论文] | 补充材料 | 正式补充版 | “Details of SiamProm”, equations 1–11; “Parameter setting” | 3-mer→79 tokens、1024 维、4-head attention、2-layer Bi-LSTM hidden 32、CNN kernel 3、128 维 compressor、margin 2、batch 256 等。 | 可访问 |
| E10 | [代码] | `srcs/model/siamprom.py`, `conf/model/siamprom.yaml`, `conf/hparams/hp.yaml` | `6b34869a1104a42acd215d5e4b47a720b357eb10` | model `SeqEmbedding`, `PromRepresentationNet.forward`, `Compressor`, `predict`; `get_attn_pad_mask` | 代码确认三支并行张量流与 `3072→512→128→32→2`；同时 ID 0=`AAA`，却被 attention 当 PAD mask。 | 可访问 |
| E11 | [冲突] | 补充公式 10 与 `srcs/data_loader.py`, `srcs/model/loss.py` | supplement + code `6b34869…` | supplement “Contrastive loss”; code `collate:24–37`, `ContrastiveLoss:8–20` | 论文定义 `c=1` 同类；代码 XOR 定义 0 同类、1 异类并交换损失项。语义编码相反，但实际仍同类拉近、异类推远。 | 可访问；冲突已解析，不改变优化方向 |
| E12 | [代码] | `srcs/trainer.py`, `srcs/model/siamprom.py` | `6b34869a1104a42acd215d5e4b47a720b357eb10` | trainer `58–70`; model `predict:244–247` | 每 batch 同时算 contrastive + classification；`predict()` 对 encoder 使用 `no_grad`，故编码器只受对比损失、分类头只受 CE 更新，不是公开描述清晰可见的两阶段。 | 可访问 |
| E13 | [论文] | 主文 Table 2，Figure 3 | 正式发表版 | PDF p.5–7 | 四种负样本 × 五模型结果；phantom 下 SiamProm Acc 88.74%、Sn 87.20%、Sp 90.30%、MCC 0.7754；SVM random/CDS 为 90.22%/88.54%。 | 可访问 |
| E14 | [论文] | 主文 Table 3 | 正式发表版 | PDF p.7 | 34 条全负类 IND 上，SiamProm 在 random/CDS/partial/phantom 训练下 Sp 为 58.82/64.70/76.47/88.23%。 | 可访问 |
| E15 | [论文] | 主文 Table 4 | 正式发表版 | PDF p.7–8 | phantom 消融：w/o Siamese Acc 82.66/MCC .6531/IND 67.64；full 为 88.74/.7754/88.23；其余删支均降分。 | 可访问 |
| E16 | [论文] | 主文 Figure 4 | 正式发表版 | “Performance on real non-promoters”, PDF p.6–7 | t-SNE 仅展示模型已有表征下的 2D 投影，并非独立外部验证。 | 可访问 |
| E17 | [论文] | 主文 Figure 5 与 “Motif analysis” | 正式发表版 | PDF p.8–9 | 作者平均/归一化 attention、筛高分 k-mer 对并计数，称 `GCGATCGC` 是新、回文、内容保守、位置漂移的潜在 promoter motif。 | 可访问 |
| E18 | [外部核验] | Naoki Sato, “Comparative Analysis of the Genomes of Cyanobacteria and Plants” | Genome Informatics 13 (2002) 173–182 | [J-STAGE PDF](https://www.jstage.jst.go.jp/article/gi1990/13/0/13_0_173/_pdf), p.176–177, section 3.1 | 至少 2002 年已精确报告 Anabaena/Nostoc/Synechocystis 的高频回文 `GCGATCGC`，且存在于 coding 与 non-coding 序列；直接否定“新序列”主张。 | 可访问 |
| E19 | [外部核验] | Xu, Lawrence & Durand, “Selection, periodicity and potential function for HIP1…” | Nucleic Acids Research 46(5), 2018, DOI `10.1093/nar/gky075` | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5861425/), abstract/results/discussion；[Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.b301d) | `GCGATCGC` 早已名为 HIP1，在蓝藻基因组超高频；该研究未发现它邻近 promoter 或参与基因表达调控的证据。 | 可访问 |
| E20 | [推断] | 官方 FASTA 的 literal motif 计数 | `6b34869a1104a42acd215d5e4b47a720b357eb10` | 对 `GCGATCGC` 做允许重叠的逐序列/逐类计数 | 正例 1,372/12,566 (10.918%) 含 HIP1；random/CDS/partial/phantom 负例分别 15/866/552/5 条（0.119/6.892/4.393/0.040%）。phantom 几乎清除 HIP1，造成类别捷径。 | 可复核；源数据可访问 |
| E21 | [外部核验] | Mitschke et al., “Dynamics of transcriptional start site selection…” | PNAS 108(50), 2011, DOI `10.1073/pnas.1112724108` | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3250118/), abstract & Computational Methods；另见 [PubMed](https://pubmed.ncbi.nlm.nih.gov/22135468/) | 13,705 是 dRNA-seq 得到的 candidate TSS 地图；以 reads/聚类阈值定义，少数区域另做 primer extension/Northern blot。论文主文误把其来源列为完整基因组文献 [20]。 | 可访问；来源冲突已解析 |
| E22 | [论文] | 主文 Discussion | 正式发表版 | PDF p.9 | 作者自己承认 `GCGATCGC` 功能未来需 biological assays；因此本文没有实验功能验证。 | 可访问 |
| E23 | [代码] | `data/7120_pseudo.fasta` | `6b34869a1104a42acd215d5e4b47a720b357eb10` | literal duplicate scan；CD-HIT-EST 0.8 得 33 clusters | 34 条 IND 中 header `sp|8` 与 `sp|9` 的 81 nt 序列完全相同；独立序列最多 33。 | 可访问并复核 |
| E24 | [缺失] | 主文、补充、官方仓库 | 正式版 + `6b34869…` | Table 2/4、supplement “Parameter setting”、repo all files | 未报告随机重复 seeds、逐折预测/方差、括号统计量的检验定义、基线调参搜索空间、Optuna 是否嵌套、硬件；仓库无完整实验驱动程序。 | 材料可访问；信息缺失 |

## 标准模式外部核验边界

本次只核验两组会改变结论的外部 claim family：

1. **正样本来源与标签强度：** 使用 Mitschke 2011 和 Kaneko 2001 的第一方记录解析 13,705 的真实来源与 candidate TSS 层级。
2. **`GCGATCGC` 的新颖性和启动子功能：** 使用 Sato 2002、Xu et al. 2018 及其官方数据记录核验精确序列、HIP1 名称、全基因组分布与既有负结果。

其余问题均由论文、补充和官方仓库内部证据解析；未扩展为领域综述。
