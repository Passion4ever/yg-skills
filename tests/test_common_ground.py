"""common-ground 技能的结构测试。

这一类技能（grill-me、catch-me-up）的价值全在「多次调用行为一致、输出标准化」。
保证一致性的手段是五段固定骨架，而骨架这种约定放在 TEMPLATE.md 里会和现实走岔，
走岔之后模板变成误导。所以把它钉成可执行的检查：加第三个技能时，缺哪一段这里会红。
"""

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMON_GROUND = ROOT / "skills" / "common-ground"

SECTIONS = ["## 怎么做", "## 输出格式", "## 完成条件"]
PREAMBLE = ["**成功标准**：", "激活期间**不做**："]


def skills() -> list[Path]:
    return sorted(p for p in COMMON_GROUND.iterdir() if p.is_dir())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split(text: str) -> tuple[dict, str]:
    """frontmatter 与正文。"""
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body


class DiscoveryTests(unittest.TestCase):
    def test_the_category_is_not_empty(self):
        """空目录会让下面每个 subTest 循环零次而全部「通过」。"""
        self.assertGreaterEqual(len(skills()), 2, "common-ground 至少应有两个技能")

    def test_every_skill_dir_has_a_skill_md_and_a_readme(self):
        for skill in skills():
            with self.subTest(skill=skill.name):
                self.assertTrue((skill / "SKILL.md").is_file())
                self.assertTrue((skill / "README.md").is_file())

    def test_the_skeleton_lives_in_skill_md_not_in_a_loaded_on_demand_file(self):
        """references/ 与 assets/ 是按需读的——模型得先决定去读。

        每次调用都必用的骨架一旦搬进去，就引入了一次「会不会去读」的抛硬币，
        而这正是要消除的不一致来源。骨架必须留在 SKILL.md 里。

        禁的是「按需加载的内容」，不是「子目录」。agents/openai.yaml 是 Codex 的
        显示名，模型从头到尾不读它，搬不走任何骨架，所以不在此列。
        """
        for skill in skills():
            with self.subTest(skill=skill.name):
                extra = sorted(p.name for p in skill.iterdir() if p.is_dir())
                self.assertEqual(
                    [d for d in extra if d != "agents"], [],
                    f"{skill.name} 把内容放进了按需加载的目录",
                )


class TemplateTests(unittest.TestCase):
    """五段骨架：成功标准 / 激活期间不做 / 怎么做 / 输出格式 / 完成条件。"""

    def test_frontmatter_name_matches_the_directory(self):
        for skill in skills():
            with self.subTest(skill=skill.name):
                front, _ = split(read(skill / "SKILL.md"))
                self.assertEqual(front["name"], skill.name)

    def test_the_preamble_states_success_and_what_it_refuses_to_do(self):
        """两句都在正文最前面——判据要出现在模型最先读到的位置。"""
        for skill in skills():
            with self.subTest(skill=skill.name):
                _, body = split(read(skill / "SKILL.md"))
                head = body.split(SECTIONS[0])[0]
                for line in PREAMBLE:
                    self.assertIn(line, head, f"{skill.name} 开头缺「{line}」")

    def test_the_three_headings_are_verbatim_and_in_order(self):
        for skill in skills():
            with self.subTest(skill=skill.name):
                _, body = split(read(skill / "SKILL.md"))
                found = re.findall(r"^## .+$", body, re.MULTILINE)
                self.assertEqual(found, SECTIONS)

    def test_the_output_section_carries_a_literal_skeleton(self):
        """散文描述格式会被重新组织，字面骨架不会。

        判据是占位符：`<...>` 是给模型照抄再填的位置。一个都没有，说明这一节
        又退回成了「先写一句话概括，然后列出……」那种描述。
        """
        for skill in skills():
            with self.subTest(skill=skill.name):
                _, body = split(read(skill / "SKILL.md"))
                section = body.split("## 输出格式")[1].split("## 完成条件")[0]
                self.assertGreaterEqual(
                    len(re.findall(r"<[^>]+>", section)), 3,
                    f"{skill.name} 的输出格式不是字面骨架",
                )
                self.assertRegex(section, re.compile(r"^### ①", re.MULTILINE))


class ExampleTests(unittest.TestCase):
    """✗ 和 ✓ 只成对出现。

    单独一个 ✗ 是禁令——只说了别做什么，没给正确形状。当失败模式是「照做了但
    输出形状不对」时，禁令会被讨价还价，正面配方不会。成对才是配方。
    """

    def test_no_bad_example_without_a_good_one_beside_it(self):
        for skill in skills():
            with self.subTest(skill=skill.name):
                for n, line in enumerate(read(skill / "SKILL.md").splitlines(), 1):
                    if "✗" in line:
                        self.assertIn("✓", line, f"{skill.name}:{n} 有 ✗ 没有 ✓")

    def test_examples_stay_outside_the_copied_skeleton(self):
        """骨架是要被逐字照抄的——例子写进去，模型会连例子一起抄进输出。"""
        for skill in skills():
            with self.subTest(skill=skill.name):
                _, body = split(read(skill / "SKILL.md"))
                section = body.split("## 输出格式")[1].split("## 完成条件")[0]
                skeleton = section.split("---")[1]
                self.assertNotIn("✗", skeleton, f"{skill.name} 的照抄区里混进了例子")


class SimplicityTests(unittest.TestCase):
    """大道至简：一句话删掉之后输出不会变，它就该删。

    量不了「会不会改变输出」，只能量影子。但影子不是全文长度——全文里最长的一段是
    「输出格式」，而那一段是骨架，越具体越好，拿总长度卡它等于奖励散文、惩罚结构。

    散文只会长在「怎么做」里（现状 5 / 15 行），所以卡那一段。全文只留一个防荒唐的上限。
    """

    HOW_LIMIT = 25
    FILE_LIMIT = 110

    def test_the_prose_section_does_not_grow_back(self):
        """grill-me 曾有一节「问什么」列六个切入角度——灵感提示，不是约束，
        删了技能照样跑，留着每次调用问的方向还会漂。这条挡的就是它重新长回来。"""
        for skill in skills():
            with self.subTest(skill=skill.name):
                _, body = split(read(skill / "SKILL.md"))
                how = body.split(SECTIONS[0])[1].split(SECTIONS[1])[0]
                n = len(how.strip().splitlines())
                self.assertLessEqual(
                    n, self.HOW_LIMIT,
                    f"{skill.name} 的「怎么做」有 {n} 行——先问哪几行删掉输出也不会变",
                )

    def test_no_skill_outgrows_the_template(self):
        for skill in skills():
            with self.subTest(skill=skill.name):
                n = len(read(skill / "SKILL.md").splitlines())
                self.assertLessEqual(n, self.FILE_LIMIT, f"{skill.name} 有 {n} 行")

    def test_manual_only_skills_do_not_advertise_dead_triggers(self):
        """disable-model-invocation 关掉的正是「模型读 description 自己启动」。

        这种技能的 description 里再写「当用户说 X 时立刻使用」，模型看不到，
        写了也不生效，只会让人误以为它能自动启动。
        """
        for skill in skills():
            with self.subTest(skill=skill.name):
                front, _ = split(read(skill / "SKILL.md"))
                if not front.get("disable-model-invocation"):
                    continue
                self.assertNotIn("立刻使用", front["description"])


if __name__ == "__main__":
    unittest.main()
