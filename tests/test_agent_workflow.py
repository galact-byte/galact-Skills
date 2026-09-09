#!/usr/bin/env python3
"""Static regression checks for the agent-workflow documentation contract."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "agent-workflow" / "SKILL.md"
SCENARIOS = ROOT / "skills" / "agent-workflow" / "references" / "scenarios.md"


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
        text,
        re.MULTILINE,
    )
    if not match:
        raise AssertionError(f"missing section: {heading}")
    return match.group(1)


class AgentWorkflowDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.scenarios = SCENARIOS.read_text(encoding="utf-8")

    def test_frontmatter_and_trigger_are_preserved(self) -> None:
        self.assertTrue(self.text.startswith("---\nname: agent-workflow\n"))
        self.assertIsNotNone(re.search(r"^description: Use when .+$", self.text, re.MULTILINE))

    def test_core_principles_define_scope_and_investigation(self) -> None:
        body = section(self.text, "核心原则")
        for phrase in ("授权范围", "实现细节", "复杂度", "先调查", "沉默", "授权也不外溢", "除非确有必要", "子代理", "推理强度", "不默认使用高档"):
            self.assertIn(phrase, body)

    def test_decision_order_distinguishes_request_modes_and_blockers(self) -> None:
        body = section(self.text, "决策顺序")
        for phrase in ("明确实施", "仅计划", "先审方案", "已完成", "未决项阻塞", "直接后续", "外部副作用"):
            self.assertIn(phrase, body)

    def test_approval_boundaries_remain_explicit(self) -> None:
        body = section(self.text, "必须先批准")
        for phrase in ("生产系统", "生产访问", "真实用户数据", "发送消息", "发布", "推送代码", "Issue/PR", "认证", "删除或覆盖", "架构或兼容性", "付费", "安装或下载"):
            self.assertIn(phrase, body)
        self.assertIn("沉默不构成批准", body)

    def test_failure_progression_and_completion_are_evidence_based(self) -> None:
        failure = section(self.text, "失败推进")
        completion = section(self.text, "完成声明")
        for phrase in ("观察", "假设", "最小验证", "连续三次", "复核", "调整方法", "盲目增加重试", "内部修复轮次", "硬性预算", "独立工作"):
            self.assertIn(phrase, failure)
        for phrase in ("交付格式", "失败路径", "生命周期", "暂缓", "轮次上限", "未完成", "证据", "模板", "敏感信息", "范围外"):
            self.assertIn(phrase, completion)

    def test_verification_and_tdd_boundaries_are_separate(self) -> None:
        verification = section(self.text, "验证强度")
        tdd = section(self.text, "TDD 边界")
        for phrase in ("最终", "代码或相关环境变化", "完整回归", "旧证据", "状态未改变", "无法确认", "静态检查", "模型行为", "退出码"):
            self.assertIn(phrase, verification)
        for phrase in ("默认", "严格 TDD", "例外", "保留既有成果", "事后补测试", "隔离副本", "不叠加", "全绿后"):
            self.assertIn(phrase, tdd)

    def test_scope_priority_and_domain_checkpoints_are_explicit(self) -> None:
        body = section(self.text, "适用范围与优先级")
        for phrase in ("Trellis", "显式领域流程", "批准节点", "不会自动接管", "不覆盖"):
            self.assertIn(phrase, body)

    def test_scenarios_are_linked_and_cover_required_cases(self) -> None:
        self.assertIn("[场景正反例](references/scenarios.md)", self.text)
        expected = {
            "明确跨文件实施", "仅计划", "显式先审方案", "部分阻塞", "普通测试失败",
            "连续失败", "已有授权", "未授权外部操作", "真实未完成",
            "代码或环境变化后的旧证据", "状态未变的已有证据", "默认风险相称测试",
            "严格 TDD", "Trellis 与领域检查点", "硬性预算与内部轮次",
            "交付模板与可追溯证据", "子代理与推理强度",
        }
        names = re.findall(r"^## 场景：(.+)$", self.scenarios, re.MULTILINE)
        self.assertEqual(len(names), len(set(names)), "duplicate scenario headings")
        self.assertTrue(expected.issubset(names), f"missing scenarios: {expected - set(names)}")
        for name in names:
            with self.subTest(scenario=name):
                body = section(self.scenarios, f"场景：{name}")
                for label in ("场景输入", "正确动作", "错误动作", "观察点"):
                    fields = re.findall(
                        rf"^### {label}\n(.*?)(?=^### |\Z)", body, re.MULTILINE | re.DOTALL
                    )
                    self.assertEqual(len(fields), 1, f"{name}: missing/duplicate {label}")
                    self.assertTrue(fields[0].strip(), f"{name}: empty {label}")

    def test_regression_is_sensitive_to_removed_guards(self) -> None:
        mutations = (
            ("test_approval_boundaries_remain_explicit", "必须先批准", "沉默不构成批准"),
            ("test_approval_boundaries_remain_explicit", "必须先批准", "生产访问"),
            ("test_verification_and_tdd_boundaries_are_separate", "TDD 边界", "保留既有成果"),
            ("test_verification_and_tdd_boundaries_are_separate", "验证强度", "完整回归"),
            ("test_failure_progression_and_completion_are_evidence_based", "失败推进", "内部修复轮次"),
            ("test_scope_priority_and_domain_checkpoints_are_explicit", "适用范围与优先级", "Trellis"),
        )
        for method, heading, guard in mutations:
            with self.subTest(guard=guard):
                body = section(self.text, heading)
                self.assertIn(guard, body)
                weakened = self.text.replace(body, body.replace(guard, ""), 1)
                probe = type(self)(method)
                probe.text = weakened
                # Run the real contract test against a memory-only mutation.
                result = unittest.TestResult()
                probe.run(result)
                self.assertFalse(result.errors, result.errors)
                self.assertEqual(len(result.failures), 1, f"undetected removal: {guard}")

    def test_scenario_check_rejects_missing_case_and_empty_field(self) -> None:
        heading = "## 场景：部分阻塞"
        self.assertIn(heading, self.scenarios)
        mutations = (
            self.scenarios.replace(heading, "## 场景：重复填充", 1),
            re.sub(r"(### 正确动作\n).*?(?=^### )", r"\1\n", self.scenarios, count=1, flags=re.MULTILINE | re.DOTALL),
        )
        for weakened in mutations:
            probe = type(self)("test_scenarios_are_linked_and_cover_required_cases")
            probe.text = self.text
            probe.scenarios = weakened
            result = unittest.TestResult()
            probe.run(result)
            self.assertFalse(result.errors, result.errors)
            self.assertGreaterEqual(len(result.failures), 1)


if __name__ == "__main__":
    unittest.main()
