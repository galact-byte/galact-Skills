"""验证可分发 Skill 的本地依赖，不联网、不执行目标测试。"""
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def distribution_errors(root: Path) -> list[str]:
    errors = []
    for skill in sorted(root.glob("*/SKILL.md")):
        for nested in skill.parent.glob("**/SKILL.md"):
            if nested != skill:
                errors.append(f"{nested.relative_to(root).as_posix()}: 嵌套 Skill 入口")
    for doc in sorted(root.rglob("*.md")):
        text = doc.read_text(encoding="utf-8")
        for dependency in re.findall(r"_knowledge/[\w.-]+|rules/[\w.-]+\.md|config\.local\.txt", text):
            errors.append(f"{doc.relative_to(root).as_posix()}: 依赖宿主私有文件 {dependency}")
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", text):
            if re.match(r"[a-zA-Z][\w+.-]*:", target) or target.startswith("#"):
                continue
            local = target.split("#", 1)[0]
            if local and not (doc.parent / local).exists():
                errors.append(f"{doc.relative_to(root).as_posix()}: 本地链接不存在 {local}")
    return errors


class DistributionTests(unittest.TestCase):
    def test_portable_skill_tree(self):
        self.assertEqual(distribution_errors(SKILLS), [])

    def test_expected_hunt_entries(self):
        for name in ("hunt-subdomain-takeover", "hunt-source-exposure", "hunt-jndi",
                     "hunt-graphql", "hunt-websocket"):
            with self.subTest(skill=name):
                entry = SKILLS / name / "SKILL.md"
                self.assertTrue(entry.is_file(), f"缺少 {entry}")
                self.assertTrue((entry.parent / "reference.md").is_file())


class DistributionFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "example"
        self.skill.mkdir()

    def write(self, name: str, text: str):
        path = self.skill / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_existing_relative_link_and_external_url_are_allowed(self):
        self.write("SKILL.md", "[参考](reference.md#details) [官方](https://example.com/guide)")
        self.write("reference.md", "# details")
        self.assertEqual(distribution_errors(self.root), [])

    def test_missing_local_reference_is_rejected(self):
        self.write("SKILL.md", "[参考](missing.md)")
        self.assertEqual(distribution_errors(self.root), ["example/SKILL.md: 本地链接不存在 missing.md"])

    def test_private_dependencies_are_rejected(self):
        for dependency in ("_knowledge/test.md", "rules/contract.md", "config.local.txt"):
            with self.subTest(dependency=dependency):
                self.write("SKILL.md", f"读取 `{dependency}`")
                self.assertEqual(distribution_errors(self.root), [
                    f"example/SKILL.md: 依赖宿主私有文件 {dependency}"
                ])

    def test_nested_entry_is_rejected(self):
        self.write("SKILL.md", "# Entry")
        self.write("nested/SKILL.md", "# Duplicate")
        self.assertEqual(distribution_errors(self.root), ["example/nested/SKILL.md: 嵌套 Skill 入口"])


if __name__ == "__main__":
    unittest.main()
