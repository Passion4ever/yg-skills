"""marketplace.json 与仓库现实的一致性。

plugin 的 skills 字段是显式路径清单，不是让加载器去扫目录。好处是 skills/ 想怎么
分类都行；代价是清单会和现实走岔——加了技能忘了登记，它不会报错，只会静默地装不上。
这里就是拿仓库当真相，反过来验清单。
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def listed() -> list[tuple[str, str]]:
    return [(p["name"], s) for p in manifest()["plugins"] for s in p["skills"]]


def on_disk() -> set[str]:
    return {
        f"./{d.relative_to(ROOT)}"
        for d in (ROOT / "skills").glob("*/*")
        if (d / "SKILL.md").is_file()
    }


class ManifestTests(unittest.TestCase):
    def test_every_listed_path_is_a_real_skill(self):
        for bundle, rel in listed():
            with self.subTest(bundle=bundle, skill=rel):
                self.assertTrue(
                    (ROOT / rel / "SKILL.md").is_file(), f"{rel} 不存在或不是技能"
                )

    def test_every_skill_in_the_repo_is_listed(self):
        """漏登记不会报错，只会装不上——所以这条比上一条更重要。"""
        missing = on_disk() - {rel for _, rel in listed()}
        self.assertEqual(missing, set(), f"这些技能没登记进任何 bundle：{sorted(missing)}")

    def test_no_skill_lands_in_two_bundles(self):
        """同一个技能装两遍，在技能列表里就会出现两次。"""
        rels = [rel for _, rel in listed()]
        dupes = {r for r in rels if rels.count(r) > 1}
        self.assertEqual(dupes, set(), f"重复登记：{sorted(dupes)}")

    def test_bundles_match_the_category_directories(self):
        """bundle 就是分类。多一个少一个，说明分类和发行单位已经不是一回事了。"""
        bundles = sorted(p["name"] for p in manifest()["plugins"])
        categories = sorted(d.name for d in (ROOT / "skills").iterdir() if d.is_dir())
        self.assertEqual(bundles, categories)


if __name__ == "__main__":
    unittest.main()
