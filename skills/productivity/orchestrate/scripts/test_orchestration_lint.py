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


if __name__ == "__main__":
    unittest.main(verbosity=2)
