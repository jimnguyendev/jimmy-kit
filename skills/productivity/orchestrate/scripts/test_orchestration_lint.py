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


if __name__ == "__main__":
    unittest.main(verbosity=2)
