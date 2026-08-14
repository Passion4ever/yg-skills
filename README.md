# yg-skills

给 Claude Code 用的技能集，分两类：**科研流程**产出文件，**协作对齐**产出共识。

## 安装

```
/plugin marketplace add Passion4ever/yg-skills
/plugin install scientific@yg-skills
/plugin install common-ground@yg-skills
```

两个 bundle 独立安装，只想要其中一个就装一个。装完重启会话。

## [`scientific`](skills/scientific/) — 科研流程

**[`sci-read-paper`](skills/scientific/sci-read-paper/)** 把一篇 AI/ML 论文读成可追溯的中文精读报告：单文件离线 HTML，八章正文加一份完整证据台账。偏蛋白、小分子与药物发现方向。不做摘要，不做翻译。

**[`sci-cn-disclosure`](skills/scientific/sci-cn-disclosure/)** 把论文稿、源码、运行结果转成中国发明专利技术交底书，权利要求逐条溯源到论文行号与源码行号。产出交底书，不产出可直接递交国知局的四件套。

这一类的共同点是**交付前必须 exit 0 的校验器**（`validate_report.py`、`check_all.py`），没过就不算写完。凡是能从固定集合里选的、能数的、能对上号的，都由程序判定。

## [`common-ground`](skills/common-ground/) — 协作对齐

**[`grill-me`](skills/common-ground/grill-me/)** 动手**前**用。一轮一轮提问，把还没想清楚的思路问到每个含糊处都有明确答案。激活期间不给方案、不写代码、不做分析，最后交一份「定下来了 / 还悬着 / 下一步」。手动触发。

**[`catch-me-up`](skills/common-ground/catch-me-up/)** 跑偏**后**用。停下所有推进工作，按固定格式重建全景，交代每一个你没点头就被当成前提的决定。你说「等一下」「我没跟上」它会自己启动。

这一类的价值全在**多次调用行为一致**，所以两个技能共用一套五段骨架，约定钉在 `tests/test_common_ground.py` 里而不是写在文档里——文档会和现实走岔，测试走岔会直接红。

## 开发

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

测试守的是结构，不是效果：骨架在不在、标题顺序对不对、坏例子有没有配好例子、marketplace 清单和仓库现实一不一致。每条约束都被反向验证过——破坏它，它必须变红。

**注意**：技能的实际行为（多次调用的输出一致性）目前没有自动化验证。

## License

MIT
