#!/usr/bin/env python3
"""Black-box tests for the dependency-free orchestration linter.

The fixtures are copied into a temporary directory.  In particular, document-coverage
mutation tests never edit the checked-in skill files; each mutation is made on its own
temporary copy and is expected to make the docs phase fail.
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
from typing import Callable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
LINTER = SCRIPT_DIR / "orchestration_lint.py"
FIXTURE_ROOT = SKILL_ROOT / "tests" / "fixtures"
CONTRACT_SOURCE = FIXTURE_ROOT / "contract.json"
PLAN_SOURCE = FIXTURE_ROOT / "plan.md"
PACKET_SOURCE = FIXTURE_ROOT / "packet.md"
HANDOFF_SOURCE = FIXTURE_ROOT / "handoff.md"
PACKET_TEMPLATE = SKILL_ROOT / "PACKET.md"


class Fixture:
    """A self-contained contract, plan, packet, and covered-doc tree."""

    def __init__(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="orchestration-lint-")
        self.root = Path(self.tempdir.name)
        self.contract_path = self.root / "contract.json"
        self.plan_path = self.root / "plan.md"
        self.packet_path = self.root / "packet.md"
        self.contract = json.loads(CONTRACT_SOURCE.read_text(encoding="utf-8"))

        self.plan_path.write_text(
            PLAN_SOURCE.read_text(encoding="utf-8")
            .replace(".orchestrate/contracts/100-orchestrate-flow-v2.json", "contract.json")
            .replace(".orchestrate/plans/100-orchestrate-flow-v2.md", "plan.md"),
            encoding="utf-8",
        )
        self.packet_path.write_text(
            PACKET_SOURCE.read_text(encoding="utf-8")
            .replace(".orchestrate/contracts/100-orchestrate-flow-v2.json", "contract.json")
            .replace(".orchestrate/plans/100-orchestrate-flow-v2.md", "plan.md"),
            encoding="utf-8",
        )

        for item in self.contract["document_coverage"]:
            for relative_file in item["files"]:
                source = FIXTURE_ROOT / relative_file
                destination = self.root / relative_file
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)

        self.contract["cycle"].update(
            {
                "plan_path": "plan.md",
                "packet_path": "packet.md",
            }
        )
        self.write_contract()

    def write_contract(self) -> None:
        self.contract_path.write_text(
            json.dumps(self.contract, indent=2) + "\n", encoding="utf-8"
        )

    def close(self) -> None:
        self.tempdir.cleanup()

    def __enter__(self) -> "Fixture":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def run(self, phase: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(LINTER),
                "--contract",
                "contract.json",
                "--plan",
                "plan.md",
                "--packet",
                "packet.md",
                "--phase",
                phase,
            ],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )


def mutate_text(path: Path, mutation: Callable[[str], str]) -> None:
    path.write_text(mutation(path.read_text(encoding="utf-8")), encoding="utf-8")


class OrchestrationLintTests(unittest.TestCase):
    def assert_pass(self, fixture: Fixture, phase: str) -> None:
        result = fixture.run(phase)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"{phase} should pass:\n{result.stdout}\n{result.stderr}",
        )
        self.assertIn("orchestration lint: PASS", result.stdout)

    def assert_fail(self, fixture: Fixture, phase: str, *errors: str) -> None:
        result = fixture.run(phase)
        output = result.stdout + result.stderr
        self.assertNotEqual(
            result.returncode,
            0,
            msg=f"{phase} should fail:\n{result.stdout}\n{result.stderr}",
        )
        for error in errors:
            self.assertIn(error, output)

    def test_valid_review_case(self) -> None:
        with Fixture() as fixture:
            self.assert_pass(fixture, "review")

    def test_valid_dispatch_case(self) -> None:
        with Fixture() as fixture:
            self.assert_pass(fixture, "dispatch")

    def test_pending_recon_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["recon_gate"][0]["status"] = "PENDING"
            fixture.write_contract()
            self.assert_fail(fixture, "review", "RECON_STATUS")

    def test_pass_recon_requires_observed_object(self) -> None:
        with Fixture() as fixture:
            fixture.contract["recon_gate"][0].pop("observed")
            fixture.write_contract()
            self.assert_fail(fixture, "review", "RECON_FIELD")

    def test_pass_recon_with_wrong_observation_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["recon_gate"][0]["observed"] = {"files": 0}
            fixture.write_contract()
            self.assert_fail(fixture, "review", "RECON_MISMATCH")

    def test_pass_recon_with_missing_expected_field_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["recon_gate"][0]["observed"] = {"summary": "checked"}
            fixture.write_contract()
            self.assert_fail(fixture, "review", "RECON_MISMATCH")

    def test_pass_recon_allows_additional_observed_evidence(self) -> None:
        with Fixture() as fixture:
            fixture.contract["recon_gate"][0]["observed"]["summary"] = "checked"
            fixture.write_contract()
            self.assert_pass(fixture, "review")

    def test_stale_plan_version_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["cycle"]["plan_version"] = "v1"
            fixture.write_contract()
            self.assert_fail(fixture, "review", "VERSION_MISMATCH")

    def test_missing_plan_acceptance_contract_metadata_is_rejected_once(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.plan_path,
                lambda text: re.sub(
                    r"^- Acceptance contract:.*$\n?", "", text, flags=re.MULTILINE
                ),
            )
            result = fixture.run("review")
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                output.count("ERROR CONTRACT_PATH: plan acceptance contract path metadata is missing"),
                1,
            )

    def test_missing_packet_acceptance_contract_metadata_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(
                    r"^- Acceptance contract:.*$\n?", "", text, flags=re.MULTILINE
                ),
            )
            self.assert_fail(fixture, "review", "CONTRACT_PATH")

    def test_duplicate_contract_acceptance_id_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["acceptance"][1]["id"] = fixture.contract["acceptance"][0]["id"]
            fixture.write_contract()
            self.assert_fail(fixture, "review", "ACCEPTANCE_DUPLICATE")

    def test_missing_acceptance_reference_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(r"^- AC-006\s*$", "", text, flags=re.MULTILINE),
            )
            self.assert_fail(fixture, "review", "ACCEPTANCE_MISSING")

    def test_duplicate_acceptance_reference_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: text.replace("- AC-001\n", "- AC-001\n- AC-001\n", 1),
            )
            self.assert_fail(fixture, "review", "ACCEPTANCE_DUPLICATE")

    def test_acceptance_reference_command_prose_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: text.replace(
                    "- AC-001\n", "- AC-001\nRun command: python3 lint.py\n", 1
                ),
            )
            self.assert_fail(fixture, "review", "ACCEPTANCE_PROSE")

    def test_packet_template_acceptance_section_is_ids_only(self) -> None:
        text = PACKET_SOURCE.read_text(encoding="utf-8")
        match = re.search(r"^##\s+Acceptance references\s*$", text, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        remainder = text[match.end() :]
        next_heading = re.search(r"^##\s+", remainder, flags=re.MULTILINE)
        section = remainder[: next_heading.start() if next_heading else len(remainder)]
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"^-\s*AC-(?:[0-9]+|<[^>]+>)$")

    def test_document_coverage_pattern_is_literal_not_regex(self) -> None:
        with Fixture() as fixture:
            fixture.contract["document_coverage"][0]["pattern"] = ".*"
            fixture.write_contract()
            self.assert_fail(fixture, "docs", "COVERAGE_MISSING")

    def test_missing_verdict_dimension_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(
                    r"^- Runtime parity verdict:.*$\n?", "", text, flags=re.MULTILINE
                ),
            )
            self.assert_fail(fixture, "review", "VERDICT_DIMENSION")

    def test_missing_runtime_fix_owner_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.contract["drift_routes"][0]["runtime_fix_owner"] = ""
            fixture.write_contract()
            self.assert_fail(fixture, "review", "DRIFT_OWNER")

    def test_unapproved_dispatch_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.plan_path,
                lambda text: re.sub(
                    r"^(\s*- Status:) APPROVED$", r"\1 DRAFT", text, flags=re.MULTILINE
                ),
            )
            self.assert_fail(fixture, "dispatch", "PLAN_APPROVAL")

    def test_missing_volume_and_budget_is_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(
                    r"^## Volume and budget\n.*?\n(?=## )", "", text, flags=re.MULTILINE | re.DOTALL
                ),
            )
            self.assert_fail(fixture, "review", "VOLUME_BUDGET")

    def test_volume_and_budget_na_requires_reason(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(r"^- N/A .*$", "- N/A", text, flags=re.MULTILINE),
            )
            self.assert_fail(fixture, "dispatch", "VOLUME_BUDGET")

    def test_volume_and_budget_placeholders_are_rejected(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(
                    r"^- N/A .*$",
                    "- Data volume: <rows at 13 months>\n- Budget: <p99>\n- Proof: <command>",
                    text,
                    flags=re.MULTILINE,
                ),
            )
            self.assert_fail(fixture, "review", "VOLUME_BUDGET")

    def test_volume_and_budget_with_numbers_passes(self) -> None:
        with Fixture() as fixture:
            mutate_text(
                fixture.packet_path,
                lambda text: re.sub(
                    r"^- N/A .*$",
                    "- Data volume: 5M ledger rows at 13 months\n"
                    "- Budget: count p99 < 50 ms\n"
                    "- Proof: EXPLAIN ANALYZE on a 5M-row seed",
                    text,
                    flags=re.MULTILINE,
                ),
            )
            self.assert_pass(fixture, "dispatch")

    def test_packet_template_has_volume_and_budget(self) -> None:
        template = (SKILL_ROOT / "PACKET.md").read_text(encoding="utf-8")
        self.assertRegex(template, r"(?m)^## Volume and budget$")
        for label in ("Data volume:", "Budget:", "Proof:"):
            self.assertIn(label, template)

    def test_every_document_coverage_pair_is_checked_in_isolation(self) -> None:
        source_bytes = {
            path: path.read_bytes()
            for item in json.loads(CONTRACT_SOURCE.read_text(encoding="utf-8"))["document_coverage"]
            for relative_file in item["files"]
            for path in [FIXTURE_ROOT / relative_file]
        }

        contract = json.loads(CONTRACT_SOURCE.read_text(encoding="utf-8"))
        pairs: list[tuple[str, str]] = [
            (item["pattern"], relative_file)
            for item in contract["document_coverage"]
            for relative_file in item["files"]
        ]
        self.assertGreater(len(pairs), 0)

        for pattern, relative_file in pairs:
            with self.subTest(concept_pattern=pattern, file=relative_file):
                with Fixture() as fixture:
                    target = fixture.root / relative_file
                    mutate_text(
                        target,
                        lambda text, pattern=pattern: re.sub(
                            re.escape(pattern), "__coverage_mutated__", text, flags=re.IGNORECASE
                        ),
                    )
                    self.assert_fail(fixture, "docs", "COVERAGE_MISSING", relative_file)

        for path, expected in source_bytes.items():
            self.assertEqual(path.read_bytes(), expected, msg=f"live file changed: {path}")


class HandoffLintTests(unittest.TestCase):
    """`--phase handoff` checks the Waiting on owner section against the decision brief form."""

    def lint(self, text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="orchestration-handoff-") as tempdir:
            path = Path(tempdir) / "HANDOFF.md"
            path.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(LINTER), "--phase", "handoff", "--handoff", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def assert_pass(self, text: str) -> None:
        result = self.lint(text)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("orchestration lint: PASS (handoff", result.stdout)

    def assert_fail(self, text: str, *codes: str) -> None:
        result = self.lint(text)
        self.assertNotEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        for code in codes:
            self.assertIn(code, result.stdout)

    @staticmethod
    def source() -> str:
        return HANDOFF_SOURCE.read_text(encoding="utf-8")

    def test_valid_brief_passes(self) -> None:
        self.assert_pass(self.source())

    def test_none_passes(self) -> None:
        self.assert_pass("# HANDOFF\n\n## Waiting on owner\nNone.\n\n## Next\n1. Continue.\n")

    def test_missing_section_is_rejected(self) -> None:
        self.assert_fail("# HANDOFF\n\n## Next\n1. Continue.\n", "OWNER_SECTION")

    def test_one_liner_questions_are_rejected(self) -> None:
        self.assert_fail(
            "# HANDOFF\n\n## Waiting on owner\n- Open the PR on the kit?\n- Accept ADR-0017?\n",
            "OWNER_FORM",
        )

    def test_empty_section_is_rejected(self) -> None:
        self.assert_fail("# HANDOFF\n\n## Waiting on owner\n\n## Next\n", "OWNER_FORM")

    def test_each_missing_part_is_rejected(self) -> None:
        for key in ("What it is", "Why now", "Options", "Recommendation", "If no answer", "Evidence"):
            with self.subTest(key=key):
                text = re.sub(r"^- " + re.escape(key) + r":.*\n", "", self.source(), flags=re.MULTILINE)
                self.assert_fail(text, "BRIEF_FIELD", key)

    def test_option_without_cost_or_effect_is_rejected(self) -> None:
        for key in ("Cost", "Effect"):
            with self.subTest(key=key):
                text = re.sub(key + r": [^.]*\.", "", self.source(), count=1)
                self.assert_fail(text, "BRIEF_OPTION_COST", key)

    def test_single_option_is_rejected(self) -> None:
        text = re.sub(r"^  - B\..*\n", "", self.source(), flags=re.MULTILINE)
        self.assert_fail(text, "BRIEF_OPTIONS")

    def test_bare_id_is_rejected(self) -> None:
        text = self.source().replace(" ADR-0017 records the daily rule;", "")
        text = text.replace("- Evidence: ", "- Evidence: ADR-0017, ")
        self.assert_fail(text, "BRIEF_BARE_ID", "ADR-0017")

    def test_short_what_it_is_is_rejected(self) -> None:
        text = re.sub(r"^- What it is:.*$", "- What it is: the cap (ADR-0017).", self.source(), flags=re.MULTILINE)
        self.assert_fail(text, "BRIEF_EXPLAIN")

    def test_question_outside_briefs_is_rejected(self) -> None:
        text = self.source().replace("## Waiting on owner\n", "## Waiting on owner\n- Accept ADR-0017?\n", 1)
        self.assert_fail(text, "OWNER_FORM", "outside")

    def test_none_alongside_a_brief_is_rejected(self) -> None:
        text = self.source().replace("## Waiting on owner\n", "## Waiting on owner\nNone.\n", 1)
        self.assert_fail(text, "OWNER_FORM", "None.")

    def test_what_it_is_length_is_language_neutral(self) -> None:
        # Values follow the owner's language. CJK has no spaces between words; Vietnamese is
        # written as escapes because the kit's language audit keeps Vietnamese out of sources.
        values = {
            "cjk": "\u9891\u7387\u4e0a\u9650\u9632\u6b62\u4e00\u4f4d\u5b66\u5458\u5728\u4e00\u5929\u5185\u6536\u5230\u592a\u591a"
            "\u8425\u9500\u6d88\u606f\uff0c\u8d85\u8fc7\u4e0a\u9650\u7684\u6d88\u606f\u4f1a\u88ab\u4e22\u5f03\u3002",
            "vietnamese": "Gi\u1edbi h\u1ea1n n\u00e0y ch\u1eb7n m\u1ed9t h\u1ecdc vi\u00ean nh\u1eadn qu\u00e1 nhi\u1ec1u tin "
            "marketing trong m\u1ed9t ng\u00e0y; tin v\u01b0\u1ee3t gi\u1edbi h\u1ea1n b\u1ecb b\u1ecf.",
        }
        for language, value in values.items():
            with self.subTest(language=language):
                text = re.sub(r"^- What it is:.*$", lambda _m, v=value: "- What it is: " + v, self.source(), flags=re.MULTILINE)
                self.assert_pass(text)
        self.assertNotIn(" ", values["cjk"])
        self.assertLess(len(values["cjk"].split()), 8)  # the old word count would have failed it
        short = "\u9891\u7387\u4e0a\u9650"
        text = re.sub(r"^- What it is:.*$", "- What it is: " + short, self.source(), flags=re.MULTILINE)
        self.assert_fail(text, "BRIEF_EXPLAIN")

    def test_placeholder_is_rejected(self) -> None:
        text = self.source().replace("- Why now: the admin card", "- Why now: <what it blocks> the admin card")
        self.assert_fail(text, "BRIEF_PLACEHOLDER")

    def test_topic_heading_is_rejected(self) -> None:
        text = re.sub(r"^### 1\..*$", "### 1. Cap", self.source(), flags=re.MULTILINE)
        self.assert_fail(text, "BRIEF_DECISION")

    def test_standard_names_are_not_ids(self) -> None:
        text = self.source().replace("- Evidence: ", "- Evidence: UTF-8 export, ")
        self.assert_pass(text)

    def test_contract_phases_still_require_their_files(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LINTER), "--phase", "review"], check=False, capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--contract", result.stderr)

    def test_resume_docs_name_the_handoff_check(self) -> None:
        text = (SKILL_ROOT / "references" / "context-and-resume.md").read_text(encoding="utf-8")
        self.assertIn("--phase handoff", text)
        self.assertIn("## Waiting on owner", text)


PACKET_ONLY = """# Packet 176 — rename-column

## Objective
{objective}

## Volume and budget
- N/A — the packet changes no query and adds no loop on a hot path.
{lines}

## Tests
{tests}
"""


class DispatchEnforcementTests(unittest.TestCase):
    """The four rules a sprint broke while nothing failed: Advisor round, executor seat, wave audit."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orchestration-enforce-")
        self.root = Path(self.tmp.name).resolve()
        (self.root / ".orchestrate" / "packets").mkdir(parents=True)
        (self.root / ".claude").mkdir()
        self.addCleanup(self.tmp.cleanup)

    tests = "- none — a column rename changes no behaviour a new test would guard."

    def config(self, **values: object) -> None:
        (self.root / ".claude" / "orchestrator.json").write_text(json.dumps(values), encoding="utf-8")

    def packet(self, objective: str = "Rename a column.", *lines: str) -> Path:
        path = self.root / ".orchestrate" / "packets" / "176-rename-column.md"
        path.write_text(
            PACKET_ONLY.format(objective=objective, lines="\n".join(lines), tests=self.tests), encoding="utf-8"
        )
        return path

    def lint(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LINTER), "--phase", "dispatch", *args],
            cwd=self.root, check=False, capture_output=True, text=True,
        )

    def assert_fails(self, result: subprocess.CompletedProcess[str], code: str) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stdout)

    def assert_passes(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # Incident 3: a packet that changed Kafka retry and rebalance semantics was dispatched with no Advisor round.
    KAFKA = "Change the consumer retry policy and the rebalance handling of the Kafka consumer."

    def test_risky_packet_without_advisor_line_is_rejected_without_a_contract(self) -> None:
        path = self.packet(self.KAFKA, "- Executor: opus")
        result = self.lint("--packet", str(path))
        self.assert_fails(result, "ADVISOR_REQUIRED")
        self.assertIn("advisor-review.sh", result.stdout)
        self.assertIn("rebalance", result.stdout)

    def test_ordinary_packet_needs_no_advisor_line(self) -> None:
        self.assert_passes(self.lint("--packet", str(self.packet("Rename a column.", "- Executor: sonnet"))))

    def test_risk_words_match_whole_words_only(self) -> None:
        text = "Block the clock skew; unlockable offsets are not a topic here."
        self.assert_passes(self.lint("--packet", str(self.packet(text.replace("offsets", "numbers"), "- Executor: sonnet"))))

    def test_risk_word_in_the_plan_also_requires_the_advisor_line(self) -> None:
        plan = self.root / "plan.md"
        plan.write_text("# Plan\nA lease with fencing tokens.\n", encoding="utf-8")
        path = self.packet("Rename a column.", "- Executor: sonnet")
        self.assert_fails(self.lint("--packet", str(path), "--plan", str(plan)), "ADVISOR_REQUIRED")

    def test_approved_verdict_needs_an_existing_review_file(self) -> None:
        review = self.root / ".orchestrate" / "plans" / "176-review.md"
        path = self.packet(self.KAFKA, "- Executor: opus", f"- Advisor: PLAN_APPROVED {review}")
        self.assert_fails(self.lint("--packet", str(path)), "ADVISOR_REQUIRED")
        review.parent.mkdir(parents=True)
        review.write_text("PLAN_APPROVED\n", encoding="utf-8")
        self.assert_passes(self.lint("--packet", str(path)))

    def test_relative_review_path_resolves_from_the_repository_root(self) -> None:
        review = self.root / ".orchestrate" / "plans" / "176-review.md"
        review.parent.mkdir(parents=True)
        review.write_text("PLAN_APPROVED\n", encoding="utf-8")
        path = self.packet(self.KAFKA, "- Executor: opus", "- Advisor: PLAN_APPROVED .orchestrate/plans/176-review.md")
        self.assert_passes(self.lint("--packet", str(path)))

    def test_plan_revise_is_not_an_approval(self) -> None:
        review = self.root / "review.md"
        review.write_text("PLAN_REVISE\n", encoding="utf-8")
        path = self.packet(self.KAFKA, "- Executor: opus", f"- Advisor: PLAN_REVISE {review}")
        self.assert_fails(self.lint("--packet", str(path)), "ADVISOR_REQUIRED")

    def test_waiver_names_who_and_why(self) -> None:
        for waiver, ok in (
            ("waived by the owner — pure rename, no behavior change", True),
            ("waived — pure rename, no behavior change", False),
            ("waived by the owner — ok", False),
        ):
            path = self.packet(self.KAFKA, "- Executor: opus", f"- Advisor: {waiver}")
            result = self.lint("--packet", str(path))
            if ok:
                self.assert_passes(result)
            else:
                self.assert_fails(result, "ADVISOR_REQUIRED")

    def test_contract_dispatch_also_requires_the_advisor_line(self) -> None:
        with Fixture() as fixture:
            mutate_text(fixture.packet_path, lambda text: text.replace("- Executor: sonnet", "- Executor: sonnet\n- Note: change the retry policy.", 1))
            OrchestrationLintTests().assert_fail(fixture, "dispatch", "ADVISOR_REQUIRED")
            OrchestrationLintTests().assert_pass(fixture, "review")

    # Incident 5: the owner pinned seats ("the root model never executes"), the root dispatched to its own model.
    def test_forbidden_executor_is_rejected(self) -> None:
        self.config(forbidden_executor_models=["fable"], executor_models={"hard": "opus", "default": "sonnet"})
        result = self.lint("--packet", str(self.packet("Rename a column.", "- Executor: fable")))
        self.assert_fails(result, "EXECUTOR_FORBIDDEN")
        self.assertIn("executor_models", result.stdout)
        self.assert_passes(self.lint("--packet", str(self.packet("Rename a column.", "- Executor: opus"))))

    def test_forbidden_model_is_found_inside_a_provider_route(self) -> None:
        self.config(forbidden_executor_models=["fable"])
        path = self.packet("Rename a column.", "- Executor: opencode run -m provider/Fable-5")
        self.assert_fails(self.lint("--packet", str(path)), "EXECUTOR_FORBIDDEN")

    def test_missing_executor_is_rejected(self) -> None:
        self.assert_fails(self.lint("--packet", str(self.packet())), "EXECUTOR_FORBIDDEN")

    # Incident 4: nine packets landed before the owner asked for the audit.
    def sprint(self, rows: int, *markers: tuple[int, str]) -> Path:
        lines = ["# Sprint", "", "| NNN | slug | state | owner |", "|---|---|---|---|"]
        for number in range(1, rows + 1):
            lines.append(f"| {number:03d} | packet-{number} | landed | root |")
            lines.extend(f"audit: {path}" for at, path in markers if at == number)
        lines.append("| 099 | next | approved | root |")
        path = self.root / ".orchestrate" / "SPRINT.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_audit_due_after_more_than_six_landed_packets(self) -> None:
        packet = self.packet("Rename a column.", "- Executor: sonnet")
        result = self.lint("--packet", str(packet), "--sprint", str(self.sprint(9)))
        self.assert_fails(result, "AUDIT_DUE")
        self.assertIn("9 packets", result.stdout)
        self.assert_passes(self.lint("--packet", str(packet), "--sprint", str(self.sprint(6))))

    def test_audit_marker_with_an_existing_report_resets_the_count(self) -> None:
        packet = self.packet("Rename a column.", "- Executor: sonnet")
        report = self.root / ".orchestrate" / "audit-1.md"
        report.write_text("health pass\n", encoding="utf-8")
        self.assert_passes(self.lint("--packet", str(packet), "--sprint", str(self.sprint(9, (4, str(report))))))
        missing = self.sprint(9, (4, str(self.root / "never-written.md")))
        self.assert_fails(self.lint("--packet", str(packet), "--sprint", str(missing)), "AUDIT_DUE")

    def test_audit_every_comes_from_orchestrator_json(self) -> None:
        packet = self.packet("Rename a column.", "- Executor: sonnet")
        self.config(audit_every=3)
        self.assert_fails(self.lint("--packet", str(packet), "--sprint", str(self.sprint(4))), "AUDIT_DUE")
        self.config(audit_every=10)
        self.assert_passes(self.lint("--packet", str(packet), "--sprint", str(self.sprint(9))))

    def test_sprint_alone_is_enough_to_check_the_audit(self) -> None:
        self.assert_fails(self.lint("--sprint", str(self.sprint(9))), "AUDIT_DUE")

    def test_packet_only_mode_still_checks_volume_and_budget(self) -> None:
        path = self.packet("Rename a column.", "- Executor: sonnet")
        path.write_text(path.read_text(encoding="utf-8").replace("## Volume and budget", "## Other"), encoding="utf-8")
        self.assert_fails(self.lint("--packet", str(path)), "VOLUME_BUDGET")

    # Incident 6: packets listed test cases in their ACs ("every finding has a vitest assertion",
    # "one case per role", 15 named route cases); executors obeyed the packet over AGENTS.md and the
    # test code grew to 91 000 Go and 40 000 SPA lines while a screen audit found 58 UX problems.
    def lint_tests(self, tests: str, objective: str = "Rename a column.") -> subprocess.CompletedProcess[str]:
        self.tests = tests
        return self.lint("--packet", str(self.packet(objective, "- Executor: sonnet")))

    @staticmethod
    def new_tests(count: int) -> str:
        return "\n".join(
            f"- new: TestRename_case{n} — guards: renamed column number {n} keeps its stored values" for n in range(count)
        )

    def test_packet_without_tests_section_is_rejected(self) -> None:
        path = self.packet("Rename a column.", "- Executor: sonnet")
        path.write_text(path.read_text(encoding="utf-8").replace("## Tests", "## Other"), encoding="utf-8")
        result = self.lint("--packet", str(path))
        self.assert_fails(result, "TESTS_SECTION")
        self.assertIn("guards:", result.stdout)

    def test_tests_section_needs_a_line_and_none_needs_a_reason(self) -> None:
        self.assert_fails(self.lint_tests(""), "TESTS_SECTION")
        self.assert_fails(self.lint_tests("- none"), "TESTS_SECTION")
        self.assert_fails(self.lint_tests("- none — rename\n" + self.new_tests(1)), "TESTS_SECTION")

    def test_new_test_must_name_the_risk_it_guards(self) -> None:
        for line in (
            "- new: TestRenameColumn",
            "- new: TestRenameColumn — guards: ok",
            "- new: <TestName> — guards: <the behaviour that breaks silently without it>",
        ):
            with self.subTest(line=line):
                self.assert_fails(self.lint_tests(line), "TEST_RISK")
        self.assert_passes(self.lint_tests(
            "- new: vitest: web/src/rename.test.ts › keeps values — guards: renamed column keeps its stored values"
        ))

    def test_two_tests_guarding_one_risk_are_rejected(self) -> None:
        line = "- new: TestRename_{} — guards: renamed column keeps its stored values"
        self.assert_fails(self.lint_tests(line.format("a") + "\n" + line.format("b")), "TEST_RISK")

    def test_more_than_three_new_tests_need_a_named_waiver(self) -> None:
        self.assert_passes(self.lint_tests(self.new_tests(3)))
        result = self.lint_tests(self.new_tests(4))
        self.assert_fails(result, "TEST_BUDGET")
        self.assertIn("waived by", result.stdout)
        self.assert_fails(self.lint_tests(self.new_tests(4) + "\ntest budget: waived by the owner — ok"), "TEST_BUDGET")
        self.assert_passes(self.lint_tests(
            self.new_tests(4) + "\ntest budget: waived by the owner — four independent stored formats migrate here"
        ))

    def test_acceptance_asking_for_a_test_per_item_is_rejected(self) -> None:
        real = (
            "## Acceptance (executor)\n"
            "- AC-002 every finding has a vitest assertion where behaviour or copy changed "
            "(role-gated rendering: one case per role)."
        )
        result = self.lint_tests(self.new_tests(1) + "\n\n" + real)
        self.assert_fails(result, "TEST_PER_ITEM")
        self.assertIn("every finding", result.stdout)
        for phrase in ("each finding gets a test", "one test per role", "a case per role", "a test for every row"):
            with self.subTest(phrase=phrase):
                self.assert_fails(self.lint_tests(f"{self.new_tests(1)}\n\n## Acceptance\n- AC-001 {phrase}."), "TEST_PER_ITEM")

    def test_per_item_wording_outside_acceptance_and_comments_is_allowed(self) -> None:
        objective = "Show every finding of the audit per role on one screen."
        tests = self.new_tests(1) + "\n<!-- never one case per role, finding or row -->"
        self.assert_passes(self.lint_tests(tests, objective))

    def test_tests_rules_run_at_contract_dispatch_only(self) -> None:
        with Fixture() as fixture:
            mutate_text(fixture.packet_path, lambda text: text.replace("## Tests", "## Other", 1))
            OrchestrationLintTests().assert_fail(fixture, "dispatch", "TESTS_SECTION")
            OrchestrationLintTests().assert_pass(fixture, "review")

    def test_packet_template_has_tests_section(self) -> None:
        text = PACKET_TEMPLATE.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^## Tests$")
        self.assertRegex(text, r"(?m)^- new: .* — guards: ")

    def test_packet_template_names_executor_and_advisor(self) -> None:
        text = PACKET_TEMPLATE.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^- Executor: ")
        self.assertRegex(text, r"(?m)^- Advisor: ")

    def test_every_non_negotiable_rule_is_in_the_rule_table(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        table = (SKILL_ROOT / "references" / "rules-and-enforcers.md").read_text(encoding="utf-8")
        section = skill.split("## Non-negotiable rules", 1)[1]
        rules = [line[2:].strip() for line in section.splitlines() if line.startswith("- ")]
        self.assertGreaterEqual(len(rules), 8)
        for rule in rules:
            self.assertIn(rule.rstrip(".").replace("`", ""), table.replace("`", ""), rule)
        for code in ("ADVISOR_REQUIRED", "AUDIT_DUE", "EXECUTOR_FORBIDDEN",
                     "TESTS_SECTION", "TEST_RISK", "TEST_BUDGET", "TEST_PER_ITEM"):
            self.assertIn(code, table)
            self.assertIn(code, LINTER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
