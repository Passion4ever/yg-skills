"""cn-disclosure 的校验器测试。

这套校验器有 94 个错误码，此前一个测试也没有。三次在 sci-read-paper 上的经验是：
一条看着没问题的检查可以永远不触发，而且只有负例测试会发现——眼睛看不出来，跑一遍
正常文档也看不出来，因为正常文档本来就不该触发它。

所以每条测试都长成同一个样子：从一份已知合格的交底书出发，只坏一处，断言那一处对应的
码真的响了。fixture 自己也是被测对象——它必须以 0 错误通过 check_all.py，否则所有负例
都失去参照。
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "cn-disclosure"
SCRIPTS = SKILL / "scripts"
FIXTURE = ROOT / "tests" / "cn-disclosure" / "outputs"
DISCLOSURE = "交底书.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(read(path))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class CheckerTests(unittest.TestCase):
    """每个负例只坏一处，断言对应的码触发。"""

    def workspace(self) -> Path:
        """A throwaway copy of the fixture — mutations must not touch the original."""
        work = Path(tempfile.mkdtemp()) / "case"
        shutil.copytree(FIXTURE, work)
        self.addCleanup(shutil.rmtree, work.parent, ignore_errors=True)
        return work

    def run_all(self, work: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "check_all.py"), DISCLOSURE],
            cwd=work, capture_output=True, text=True,
        )

    def codes(self, work: Path) -> set[str]:
        result = self.run_all(work)
        return set(re.findall(r"\b([A-Z][A-Z0-9_]{4,})\b", result.stdout + result.stderr))

    # -- the baseline the negatives are measured against --------------------
    def test_the_fixture_itself_passes(self):
        """Without a document that passes, no failure below means anything."""
        work = self.workspace()
        result = self.run_all(work)
        self.assertEqual(
            result.returncode, 0,
            f"the known-good disclosure no longer passes:\n{result.stdout}",
        )

    def test_check_all_exit_code_tracks_errors_not_warnings(self):
        """The fixture carries four genuine warnings and must still exit 0; one
        injected error must flip it."""
        work = self.workspace()
        self.assertEqual(self.run_all(work).returncode, 0)
        self.assertIn("WARNING", self.run_all(work).stdout)

        (work / "evidence.json").unlink()
        self.assertEqual(self.run_all(work).returncode, 1)


def mutation(name: str, code: str):
    """Register one negative case: apply a mutation, expect one code."""

    def wrap(fn):
        def test(self):
            work = self.workspace()
            fn(self, work)
            observed = self.codes(work)
            self.assertIn(
                code, observed,
                f"{name}: expected {code}, got {sorted(observed)}",
            )
        test.__name__ = f"test_{fn.__name__}"
        test.__doc__ = f"{name} → {code}"
        setattr(CheckerTests, test.__name__, test)
        return fn

    return wrap


# --- 完整性 ---------------------------------------------------------------
@mutation("表头删掉发明人", "HEADER_INCOMPLETE")
def header_missing(self, work):
    path = work / DISCLOSURE
    # the word appears three times in the header region; removing one row leaves it
    path.write_text(read(path).replace("发明人", "申报人"), encoding="utf-8")


@mutation("删掉公开充分性声明", "NO_SUFFICIENCY_DECL")
def no_sufficiency(self, work):
    path = work / DISCLOSURE
    text = read(path)
    text = re.sub(r"\*\*公开充分性声明.*?\n", "", text, flags=re.DOTALL, count=1)
    path.write_text(text.replace("核准", "确认"), encoding="utf-8")


@mutation("evidence.json 不存在", "NO_EVIDENCE_LEDGER")
def no_ledger_file(self, work):
    (work / "evidence.json").unlink()


@mutation("evidence.json 清空 claim_feature_map", "EVIDENCE_INCOMPLETE")
def empty_required_key(self, work):
    data = load(work / "evidence.json")
    data["claim_feature_map"] = []
    dump(work / "evidence.json", data)


@mutation("删掉说明书的法定一节", "SPEC_PART_MISSING")
def spec_part_missing(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("## 附图说明", "## 图的说明"), encoding="utf-8")


@mutation("删掉可替代实施方式一节", "NO_ALT_SECTION")
def no_alt_section(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("## 可替代实施方式", "## 其它写法"), encoding="utf-8")


@mutation("附图文件缺失", "FIGURE_MISSING")
def figure_file_missing(self, work):
    (work / "figures" / "fig1.png").unlink()


@mutation("正文残留待确认标记", "PENDING_CONFIRMATION")
def pending_marker(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("窗长取 128", "窗长取 [待确认:128?]"), encoding="utf-8")


# --- 权项结构 -------------------------------------------------------------
@mutation("权项编号跳号", "NUMBER_SEQUENCE")
def claim_number_gap(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("\n2. 根据权利要求 1", "\n5. 根据权利要求 1"), encoding="utf-8")


@mutation("从属权项引用在后的权项", "FORWARD_REFERENCE")
def forward_reference(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("2. 根据权利要求 1 所述", "2. 根据权利要求 4 所述"), encoding="utf-8")


@mutation("权项引用不存在的编号", "UNKNOWN_REFERENCE")
def unknown_reference(self, work):
    path = work / DISCLOSURE
    text = read(path)
    # the code fires on a reference to a lower number that is absent, so the gap
    # has to exist first — a reference to a higher number is FORWARD_REFERENCE
    text = text.replace("2. 根据权利要求 1 所述的方法，其特征在于，步骤 2）中的残差能量由重构误差的二范数给出。\n\n", "")
    text = text.replace("3. 一种计算机可读存储介质，其上存储有计算机程序，其特征在于，该程序被处理器执行时实现权利要求 1 所述的方法。",
                        "3. 一种计算机可读存储介质，其上存储有计算机程序，其特征在于，该程序被处理器执行时实现权利要求 2 所述的方法。")
    path.write_text(text, encoding="utf-8")


@mutation("权项写进宣传性用语", "PROMO_LANGUAGE")
def promo_language(self, work):
    path = work / DISCLOSURE
    path.write_text(
        read(path).replace("并输出带时间戳的异常区间。", "并输出带时间戳的异常区间，效果更好。"),
        encoding="utf-8",
    )


@mutation("独权末端落在空话上", "VAGUE_FINAL_RESULT")
def vague_final_result(self, work):
    path = work / DISCLOSURE
    path.write_text(
        read(path).replace("并输出带时间戳的异常区间。", "并输出设计结果。"),
        encoding="utf-8",
    )


@mutation("权项残留占位标记", "PLACEHOLDER")
def claim_placeholder(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("阈值 T 的窗口", "阈值 [待确认:T] 的窗口"), encoding="utf-8")


# --- 证据台账 -------------------------------------------------------------
@mutation("证据 ID 不合编号规范", "SOURCE_ID")
def bad_source_id(self, work):
    data = load(work / "evidence.json")
    data["source_map"][0]["id"] = "X1"
    dump(work / "evidence.json", data)


@mutation("两条来源用同一个 ID", "DUPLICATE_SOURCE_ID")
def duplicate_source_id(self, work):
    data = load(work / "evidence.json")
    data["source_map"][1]["id"] = data["source_map"][0]["id"]
    dump(work / "evidence.json", data)


@mutation("来源没有定位", "SOURCE_LOCATOR")
def no_locator(self, work):
    data = load(work / "evidence.json")
    data["source_map"][0]["locator"] = ""
    dump(work / "evidence.json", data)


@mutation("支持状态不在词表内", "SUPPORT_STATUS")
def bad_support_status(self, work):
    data = load(work / "evidence.json")
    data["evidence_ledger"][0]["support_status"] = "probably"
    dump(work / "evidence.json", data)


@mutation("可写入权项的条目没有来源", "MISSING_SOURCE_LINK")
def claimable_without_source(self, work):
    data = load(work / "evidence.json")
    data["evidence_ledger"][0]["source_ids"] = []
    dump(work / "evidence.json", data)


@mutation("引用不存在的来源 ID", "UNKNOWN_SOURCE_ID")
def unknown_source_id(self, work):
    data = load(work / "evidence.json")
    data["evidence_ledger"][0]["source_ids"] = ["P999"]
    dump(work / "evidence.json", data)


@mutation("降级为 needs-confirmation 却不写查过哪些", "UNDOCUMENTED_DOWNGRADE")
def undocumented_downgrade(self, work):
    data = load(work / "evidence.json")
    for item in data["evidence_ledger"]:
        if item.get("support_status") == "needs-confirmation":
            item["note"] = "没查到"
    dump(work / "evidence.json", data)


@mutation("把 needs-confirmation 的特征写进权项", "UNCLAIMABLE_IN_CLAIM")
def unclaimable_in_claim(self, work):
    data = load(work / "evidence.json")
    data["claim_feature_map"].append(
        {"claim_number": 1, "feature": "以温度补偿替代滑动窗口", "evidence_ids": ["E005"]}
    )
    dump(work / "evidence.json", data)


@mutation("权项映射引用不存在的证据", "UNKNOWN_EVIDENCE_ID")
def unknown_evidence_id(self, work):
    data = load(work / "evidence.json")
    data["claim_feature_map"][0]["evidence_ids"] = ["E999"]
    dump(work / "evidence.json", data)


@mutation("有权项没有任何特征映射", "CLAIM_NOT_MAPPED")
def claim_not_mapped(self, work):
    data = load(work / "evidence.json")
    data["claim_feature_map"] = [m for m in data["claim_feature_map"] if m["claim_number"] != 2]
    dump(work / "evidence.json", data)


@mutation("目录清点为空", "NO_INVENTORY")
def no_inventory(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["inventory"] = {}
    dump(work / "evidence.json", data)


@mutation("目录列出但未表态", "INVENTORY_UNDECIDED")
def inventory_undecided(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["inventory"]["tools/"] = ""
    dump(work / "evidence.json", data)


@mutation("没查在先申请", "NO_PRIOR_FILING_CHECK")
def no_prior_filing(self, work):
    data = load(work / "evidence.json")
    del data["metadata"]["prior_filings"]
    dump(work / "evidence.json", data)


@mutation("查了在先申请但没留检索式", "PRIOR_FILING_NO_TRACE")
def prior_filing_no_trace(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["prior_filings"] = {"searched": ""}
    dump(work / "evidence.json", data)


@mutation("检索到在先申请", "PRIOR_FILING_FOUND")
def prior_filing_found(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["prior_filings"] = [{"pub": "CN123456789A", "claim1": "一种传感器异常检测方法"}]
    dump(work / "evidence.json", data)


@mutation("记了不一致却没立待确认项", "DISCREPANCY_NO_QUESTION")
def discrepancy_no_question(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["discrepancies"][0]["question"] = ""
    dump(work / "evidence.json", data)


@mutation("主文档没有逐节表态", "NO_SOURCE_COVERAGE")
def no_source_coverage(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["source_coverage"] = {}
    dump(work / "evidence.json", data)


@mutation("有章节列出但未表态", "COVERAGE_UNDECIDED")
def coverage_undecided(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["source_coverage"]["§6 附录"] = ""
    dump(work / "evidence.json", data)


@mutation("有源码却没做自由深读", "NO_ANOMALY_PASS")
def no_anomaly_pass(self, work):
    data = load(work / "evidence.json")
    del data["metadata"]["anomalies"]
    dump(work / "evidence.json", data)


@mutation("缺 inventor_questions 数组", "NO_QUESTIONS_KEY")
def no_questions_key(self, work):
    data = load(work / "evidence.json")
    del data["inventor_questions"]
    dump(work / "evidence.json", data)


# --- 保障记录（本次新增的五个码）------------------------------------------
@mutation("完全没有保障记录", "NO_ASSURANCE_RECORD")
def no_assurance(self, work):
    data = load(work / "evidence.json")
    del data["metadata"]["assurance"]
    dump(work / "evidence.json", data)


@mutation("保障记录缺 done 字段", "ASSURANCE_INCOMPLETE")
def assurance_incomplete(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["assurance"]["external_review"] = {"model": "x"}
    dump(work / "evidence.json", data)


@mutation("跳过了却不写原因", "ASSURANCE_NO_REASON")
def assurance_no_reason(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["assurance"]["patent_search"] = {"done": False}
    dump(work / "evidence.json", data)


@mutation("跳过并写明原因", "ASSURANCE_SKIPPED")
def assurance_skipped(self, work):
    pass  # the fixture already skips patent search with a reason


@mutation("做了外部评审却不记模型", "ASSURANCE_NO_MODEL")
def assurance_no_model(self, work):
    data = load(work / "evidence.json")
    data["metadata"]["assurance"]["external_review"] = {"done": True}
    dump(work / "evidence.json", data)


# --- 可替代实施方式 -------------------------------------------------------
@mutation("处置类型不在词表内", "DISPOSITION")
def bad_disposition(self, work):
    data = load(work / "alternatives.json")
    data["choices"][0]["disposition"] = "maybe"
    dump(work / "alternatives.json", data)


@mutation("状态不在词表内", "STATUS")
def bad_status(self, work):
    data = load(work / "alternatives.json")
    data["choices"][0]["status"] = "verified"
    dump(work / "alternatives.json", data)


@mutation("两个选择用同一个 ID", "DUPLICATE_ID")
def duplicate_choice_id(self, work):
    data = load(work / "alternatives.json")
    data["choices"][1]["id"] = data["choices"][0]["id"]
    dump(work / "alternatives.json", data)


@mutation("选择没有出处", "NO_LOCUS")
def no_locus(self, work):
    data = load(work / "alternatives.json")
    data["choices"][0]["locus"] = ""
    dump(work / "alternatives.json", data)


@mutation("给了替代方案却没有依据", "NO_BASIS")
def no_basis(self, work):
    data = load(work / "alternatives.json")
    data["choices"][0]["basis"] = ""
    dump(work / "alternatives.json", data)


@mutation("标 essential 却不说理由", "NO_REASON")
def no_reason(self, work):
    data = load(work / "alternatives.json")
    for choice in data["choices"]:
        if choice["disposition"] == "essential":
            choice["reason"] = ""
    dump(work / "alternatives.json", data)


@mutation("权项数值没有处置", "UNDISPOSED_CLAIM_VALUES")
def undisposed_claim_values(self, work):
    data = load(work / "alternatives.json")
    data["choices"] = [c for c in data["choices"] if c["id"] != "A000"]
    dump(work / "alternatives.json", data)


# --- 附图 -----------------------------------------------------------------
@mutation("附图声明与插图数量对不上", "FIGURE_NOT_DECLARED")
def figure_not_declared(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("图 2 为滑动窗口切分的示意图。", ""), encoding="utf-8")


@mutation("声明了图却从不引用", "FIGURE_NEVER_REFERENCED")
def figure_never_referenced(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("切分方式如图 2 所示", "切分方式见下"), encoding="utf-8")


@mutation("附图标记编号断号", "NUMERAL_GAP")
def numeral_gap(self, work):
    path = work / DISCLOSURE
    path.write_text(read(path).replace("3—残差能量计算模块；", ""), encoding="utf-8")


@mutation("附图标记在正文里没出现", "NUMERAL_NOT_IN_TEXT")
def numeral_not_in_text(self, work):
    path = work / DISCLOSURE
    path.write_text(
        read(path).replace("5—异常区间输出", "5—异常区间输出；6—备用电源"),
        encoding="utf-8",
    )


@mutation("spec 里下标写成裸下划线", "RAW_SUBSCRIPT")
def raw_subscript(self, work):
    spec = work / "figures" / "specs" / "fig1.json"
    data = load(spec)
    data["nodes"][1]["label"] = "滑动切分 L_w"
    dump(spec, data)


class CoverageTests(unittest.TestCase):
    """哪些码还没有被任何测试覆盖 —— 让缺口可见，而不是让它安静。"""

    def defined_codes(self) -> set[str]:
        codes: set[str] = set()
        for script in SCRIPTS.glob("check_*.py"):
            codes |= set(re.findall(r"'([A-Z][A-Z0-9_]{4,})'", read(script)))
        return codes - {"ERROR", "WARNING"}

    def gather_tested_codes(self) -> set[str]:
        return set(re.findall(r'@mutation\("[^"]*", "([A-Z][A-Z0-9_]+)"\)', read(Path(__file__))))

    def test_every_new_assurance_code_is_covered(self):
        """The codes added with the assurance record must all have a negative case."""
        added = {
            "NO_ASSURANCE_RECORD", "ASSURANCE_INCOMPLETE", "ASSURANCE_NO_REASON",
            "ASSURANCE_SKIPPED", "ASSURANCE_NO_MODEL",
        }
        self.assertLessEqual(added, self.gather_tested_codes())
        self.assertLessEqual(added, self.defined_codes(), "a code was renamed in the checker")

    def test_coverage_is_reported_not_hidden(self):
        """Not a pass/fail bar — it prints what is still unguarded, so the number
        cannot quietly drift down."""
        defined, tested = self.defined_codes(), self.gather_tested_codes()
        missing = sorted(defined - tested)
        print(
            f"\n  cn-disclosure 错误码覆盖：{len(tested & defined)}/{len(defined)}"
            f"，未覆盖 {len(missing)} 个：\n    " + ", ".join(missing)
        )
        self.assertLessEqual(
            len(missing), len(defined) * 0.6,
            "coverage fell below 40% — new codes are landing without negative cases",
        )


if __name__ == "__main__":
    unittest.main()
