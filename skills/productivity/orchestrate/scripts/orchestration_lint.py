#!/usr/bin/env python3
"""Dependency-free validation for contract-backed orchestration cycles and owner decision briefs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "orchestrate.contract.v1"
AC_ID = re.compile(r"^AC-[0-9]+$")
RG_ID = re.compile(r"^RG-[0-9]+$")
BRIEF_KEYS = ("What it is", "Why now", "Options", "Recommendation", "If no answer", "Evidence")
# Ids an owner may not know: ADR-0017, PR #12, MR !34, #123, !34, a ticket key such as ABC-42.
BRIEF_ID = re.compile(
    r"\bADR[- ]?[0-9]+\b|\b(?:PR|MR)\s*[#!]?[0-9]+\b|(?<![\w/])[#!][0-9]+\b|\b[A-Z][A-Z0-9]{1,9}-[0-9]+\b"
)
# Standard names that look like ticket keys but need no explanation.
BRIEF_ID_ALLOWED = re.compile(r"^(?:UTF|SHA|ISO|HTTP|TLS|UTC|GMT|MD|BASE)-?[0-9]+$", re.IGNORECASE)


class Linter:
    def __init__(self, contract_path: Path, plan_path: Path, packet_path: Path, phase: str) -> None:
        self.contract_path = contract_path
        self.plan_path = plan_path
        self.packet_path = packet_path
        self.phase = phase
        self.errors: list[str] = []
        self.contract: dict[str, Any] = {}
        self.plan = ""
        self.packet = ""

    def error(self, code: str, message: str) -> None:
        self.errors.append(f"{code}: {message}")

    @staticmethod
    def resolved(value: str | Path) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else (Path.cwd() / path)

    @staticmethod
    def field(pattern: str, text: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    def load(self) -> None:
        try:
            parsed = json.loads(self.contract_path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                self.error("CONTRACT_SHAPE", "contract root must be an object")
            else:
                self.contract = parsed
        except (OSError, json.JSONDecodeError) as exc:
            self.error("CONTRACT_READ", f"cannot read contract: {exc}")

        for label, path in (("plan", self.plan_path), ("packet", self.packet_path)):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                self.error("FILE_READ", f"cannot read {label} file: {exc}")
                text = ""
            if label == "plan":
                self.plan = text
            else:
                self.packet = text

    def validate_contract_shape(self) -> None:
        if self.contract.get("schema_version") != SCHEMA_VERSION:
            self.error("SCHEMA_VERSION", f"schema_version must be {SCHEMA_VERSION!r}")

        cycle = self.contract.get("cycle")
        if not isinstance(cycle, dict):
            self.error("CYCLE_SHAPE", "cycle must be an object")
            cycle = {}
        for key in ("id", "slug", "plan_path", "plan_version", "packet_path"):
            if not isinstance(cycle.get(key), str) or not cycle[key].strip():
                self.error("CYCLE_FIELD", f"cycle.{key} must be a non-empty string")

        for key, prefix, pattern in (
            ("recon_gate", "RECON", RG_ID),
            ("acceptance", "ACCEPTANCE", AC_ID),
        ):
            entries = self.contract.get(key)
            if not isinstance(entries, list):
                self.error(f"{prefix}_SHAPE", f"{key} must be an array")
                continue
            seen: set[str] = set()
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    self.error(f"{prefix}_ENTRY", f"{key}[{index}] must be an object")
                    continue
                ident = entry.get("id")
                if not isinstance(ident, str) or not pattern.fullmatch(ident):
                    self.error(f"{prefix}_ID", f"{key}[{index}].id is not a valid {prefix.lower()} ID")
                elif ident in seen:
                    self.error(f"{prefix}_DUPLICATE", f"duplicate {ident}")
                else:
                    seen.add(ident)

                if key == "recon_gate" and str(entry.get("status", "")).upper() == "PASS":
                    for field in ("claim", "command"):
                        value = entry.get(field)
                        if not isinstance(value, str) or not value.strip():
                            self.error("RECON_FIELD", f"recon_gate[{index}].{field} must be non-empty for PASS")
                    for field in ("expected", "observed"):
                        value = entry.get(field)
                        if not isinstance(value, dict) or not value:
                            self.error("RECON_FIELD", f"recon_gate[{index}].{field} must be a non-empty object for PASS")

                if key == "acceptance":
                    if not isinstance(entry.get("command"), str) or not entry["command"].strip():
                        self.error("ACCEPTANCE_COMMAND", f"acceptance[{index}].command must be non-empty")
                    expected = entry.get("expected")
                    if not isinstance(expected, dict) or not isinstance(expected.get("exit_code"), int):
                        self.error("ACCEPTANCE_EXPECTED", f"acceptance[{index}].expected.exit_code must be an integer")

        routes = self.contract.get("drift_routes")
        if not isinstance(routes, list):
            self.error("DRIFT_SHAPE", "drift_routes must be an array")
        else:
            required = ("class", "actions", "evidence_owner", "runtime_fix_owner", "allowance_policy")
            for index, route in enumerate(routes):
                if not isinstance(route, dict):
                    self.error("DRIFT_ENTRY", f"drift_routes[{index}] must be an object")
                    continue
                for key in required:
                    value = route.get(key)
                    missing = value is None or (isinstance(value, str) and not value.strip())
                    if key == "actions":
                        missing = not isinstance(value, list) or not value or any(
                            not isinstance(action, str) or not action.strip() for action in value
                        )
                    if missing:
                        self.error("DRIFT_OWNER", f"drift_routes[{index}].{key} is required")

        coverage = self.contract.get("document_coverage")
        if not isinstance(coverage, list):
            self.error("COVERAGE_SHAPE", "document_coverage must be an array")
        else:
            for index, item in enumerate(coverage):
                if not isinstance(item, dict):
                    self.error("COVERAGE_ENTRY", f"document_coverage[{index}] must be an object")
                    continue
                if not isinstance(item.get("concept"), str) or not item["concept"].strip():
                    self.error("COVERAGE_CONCEPT", f"document_coverage[{index}].concept is required")
                if not isinstance(item.get("pattern"), str) or not item["pattern"]:
                    self.error("COVERAGE_PATTERN", f"document_coverage[{index}].pattern is required")
                files = item.get("files")
                if not isinstance(files, list) or not files or any(
                    not isinstance(file, str) or not file.strip() for file in files
                ):
                    self.error("COVERAGE_FILES", f"document_coverage[{index}].files must be non-empty")

    def validate_metadata(self) -> None:
        cycle = self.contract.get("cycle")
        if not isinstance(cycle, dict):
            return

        for key, actual in (("plan_path", self.plan_path), ("packet_path", self.packet_path)):
            value = cycle.get(key)
            if isinstance(value, str) and self.resolved(value) != actual.resolve():
                self.error("PATH_MISMATCH", f"cycle.{key} does not match supplied {key[:-5]} path")

        plan_version = self.field(r"^\s*-\s*Version:\s*`?([^`\s]+)", self.plan)
        if plan_version != cycle.get("plan_version"):
            self.error("VERSION_MISMATCH", "contract plan_version does not match plan metadata")

        packet_plan = re.search(
            r"^\s*-\s*Canonical plan:\s*`?([^`,]+)`?\s*,\s*version\s*`?([^`\s]+)",
            self.packet,
            re.IGNORECASE | re.MULTILINE,
        )
        if not packet_plan:
            self.error("PACKET_METADATA", "packet canonical plan/version metadata is missing")
        else:
            if self.resolved(packet_plan.group(1).strip()) != self.resolved(str(cycle.get("plan_path", ""))):
                self.error("PATH_MISMATCH", "packet canonical plan path does not match contract")
            if packet_plan.group(2).strip() != cycle.get("plan_version"):
                self.error("VERSION_MISMATCH", "packet canonical plan version does not match contract")

        plan_contract = self.field(r"^\s*-\s*Acceptance contract:\s*`?([^`\s]+)", self.plan)
        if not plan_contract:
            self.error("CONTRACT_PATH", "plan acceptance contract path metadata is missing")
        elif self.resolved(plan_contract) != self.contract_path.resolve():
            self.error("CONTRACT_PATH", "plan acceptance contract path does not match supplied contract")
        packet_contract = self.field(r"^\s*-\s*Acceptance contract:\s*`?([^`\s]+)", self.packet)
        if not packet_contract:
            self.error("CONTRACT_PATH", "packet acceptance contract path metadata is missing")
        elif self.resolved(packet_contract) != self.contract_path.resolve():
            self.error("CONTRACT_PATH", "packet acceptance contract path does not match supplied contract")

        slug_key = re.sub(r"[^a-z0-9]", "", str(cycle.get("slug", "")).lower())

        def heading_matches(kind: str, text: str) -> bool:
            match = re.search(r"^#\s*" + kind + r"\s+(\S+)(?:\s+[—-]\s+(.+))?$", text, re.IGNORECASE | re.MULTILINE)
            if not match or match.group(1) != str(cycle.get("id", "")):
                return False
            tail = re.sub(r"[^a-z0-9]", "", (match.group(2) or "").lower())
            return not slug_key or tail == slug_key

        if not heading_matches("Plan", self.plan):
            self.error("PLAN_METADATA", "plan heading does not match cycle id/slug")
        if not heading_matches("Packet", self.packet):
            self.error("PACKET_METADATA", "packet heading does not match cycle id/slug")

    @staticmethod
    def section(text: str, title: str) -> str | None:
        match = re.search(r"^##\s*" + re.escape(title) + r"\s*$", text, re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        remainder = text[match.end() :]
        next_heading = re.search(r"^##\s+", remainder, re.IGNORECASE | re.MULTILINE)
        return remainder[: next_heading.start() if next_heading else len(remainder)]

    def acceptance_refs(self, label: str, text: str) -> list[str]:
        body = self.section(text, "Acceptance references")
        if body is None:
            self.error("ACCEPTANCE_REFERENCES", f"{label} acceptance references section is missing")
            return []
        refs: list[str] = []
        for line_number, line in enumerate(body.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            match = re.fullmatch(r"-\s*(AC-[0-9]+)", stripped, re.IGNORECASE)
            if not match:
                self.error(
                    "ACCEPTANCE_PROSE",
                    f"{label} acceptance references line {line_number} must contain only an AC ID",
                )
                continue
            ident = match.group(1).upper()
            if ident in refs:
                self.error("ACCEPTANCE_DUPLICATE", f"{label} references {ident} more than once")
            refs.append(ident)
        return refs

    def validate_recon(self) -> None:
        entries = self.contract.get("recon_gate")
        if not isinstance(entries, list):
            return
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            status = str(entry.get("status", "")).upper()
            if status == "PASS":
                expected, observed = entry.get("expected"), entry.get("observed")
                if isinstance(expected, dict) and isinstance(observed, dict):
                    for field, value in expected.items():
                        if field not in observed or observed[field] != value:
                            self.error("RECON_MISMATCH", f"recon_gate[{index}].observed.{field} does not match expected evidence")
                continue
            if status == "N/A":
                reason = entry.get("reason") or entry.get("rationale") or entry.get("justification")
                observed = entry.get("observed")
                if not reason and isinstance(observed, dict):
                    reason = observed.get("reason") or observed.get("summary")
                if not isinstance(reason, str) or not reason.strip():
                    self.error("RECON_REASON", f"recon_gate[{index}] N/A requires a reason")
                continue
            self.error("RECON_STATUS", f"recon_gate[{index}] status must be PASS or reasoned N/A")

    def validate_verdicts(self) -> None:
        body = self.section(self.packet, "Verdict dimensions")
        if body is None:
            self.error("VERDICT_SECTION", "packet verdict dimensions section is missing")
            return
        labels = {
            "implementation": r"implementation\s+verdict",
            "evidence": r"evidence\s+verdict",
            "runtime parity": r"runtime[\s-]+parity\s+verdict",
            "release": r"release\s+verdict",
            "landing": r"landing\s+verdict",
        }
        for name, pattern in labels.items():
            if not re.search(pattern, body, re.IGNORECASE):
                self.error("VERDICT_DIMENSION", f"packet is missing {name} verdict")

    def validate_volume_budget(self) -> None:
        """A packet states the data volume and budget it is built for, or why none applies."""
        body = self.section(self.packet, "Volume and budget")
        if body is None:
            self.error("VOLUME_BUDGET", "packet Volume and budget section is missing")
            return
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines:
            self.error("VOLUME_BUDGET", "packet Volume and budget section is empty")
            return
        not_applicable = re.match(r"^-?\s*`?N/A`?\s*[:\-\u2014]*\s*(.*)$", lines[0], re.IGNORECASE)
        if not_applicable:
            if len(re.findall(r"[A-Za-z]", not_applicable.group(1))) < 10:
                self.error("VOLUME_BUDGET", "Volume and budget N/A requires a reason")
            return
        for label in ("Data volume", "Budget", "Proof"):
            value = self.field(r"^\s*-\s*" + label + r":\s*(.*)$", body)
            if not value or re.fullmatch(r"<[^>]*>", value) or len(re.findall(r"[A-Za-z0-9]", value)) < 3:
                self.error("VOLUME_BUDGET", f"Volume and budget is missing a measured {label.lower()}")

    def validate_docs(self) -> None:
        coverage = self.contract.get("document_coverage")
        if not isinstance(coverage, list):
            return
        for index, item in enumerate(coverage):
            if not isinstance(item, dict):
                continue
            pattern = item.get("pattern")
            files = item.get("files")
            if not isinstance(pattern, str) or not isinstance(files, list):
                continue
            try:
                folded_pattern = pattern.casefold()
            except AttributeError:
                self.error("COVERAGE_PATTERN", f"document_coverage[{index}].pattern must be text")
                continue
            for file in files:
                if not isinstance(file, str):
                    continue
                path = self.resolved(file)
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError as exc:
                    self.error("COVERAGE_FILE", f"cannot read {file}: {exc}")
                    continue
                if folded_pattern not in text.casefold():
                    self.error(
                        "COVERAGE_MISSING",
                        f"concept {item.get('concept', '<unnamed>')} pattern {pattern!r} missing from {file}",
                    )

    def run(self) -> int:
        self.load()
        self.validate_contract_shape()
        self.validate_metadata()
        self.validate_recon()

        expected = {
            str(item.get("id")).upper()
            for item in self.contract.get("acceptance", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        plan_refs = self.acceptance_refs("plan", self.plan)
        packet_refs = self.acceptance_refs("packet", self.packet)
        for label, refs in (("plan", plan_refs), ("packet", packet_refs)):
            actual = set(refs)
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            if missing:
                self.error("ACCEPTANCE_MISSING", f"{label} is missing: {', '.join(missing)}")
            if extra:
                self.error("ACCEPTANCE_EXTRA", f"{label} has unknown IDs: {', '.join(extra)}")

        self.validate_verdicts()
        if self.phase in ("review", "dispatch"):
            self.validate_volume_budget()
        if self.phase == "dispatch":
            plan_status = self.field(r"^\s*-\s*Status:\s*`?([^`\s]+)", self.plan)
            if (plan_status or "").upper() != "APPROVED":
                self.error("PLAN_APPROVAL", "dispatch requires plan Status: APPROVED")
            packet_status = self.field(r"^\s*-\s*Approval state:\s*`?([^`\s]+)", self.packet)
            if (packet_status or "").upper() != "APPROVED":
                self.error("PACKET_APPROVAL", "dispatch requires packet Approval state: APPROVED")
        if self.phase == "docs":
            self.validate_docs()

        if self.errors:
            for error in self.errors:
                print(f"ERROR {error}")
            print(f"orchestration lint: FAIL ({len(self.errors)} error(s))")
            return 1
        print(f"orchestration lint: PASS ({self.phase})")
        return 0


def lint_handoff(path: Path) -> int:
    """Check the `Waiting on owner` section of a HANDOFF file against the decision brief form.

    The form is defined by skill `ketchup` (references/decision-brief.md): one `###` per decision,
    keys in English, every key filled, at least two options with Cost and Effect, and every id used
    in a brief introduced in its `What it is` line. `None.` means nothing waits.
    """
    errors: list[str] = []

    def error(code: str, message: str) -> None:
        errors.append(f"{code}: {message}")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        error("FILE_READ", f"cannot read handoff file: {exc}")
        text = ""
    body = Linter.section(text, "Waiting on owner")
    if body is None and not errors:
        error("OWNER_SECTION", "handoff has no '## Waiting on owner' section; write 'None.' when nothing waits")
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.DOTALL)
    parts = re.split(r"^###\s+", body, flags=re.MULTILINE)
    preamble, briefs = parts[0], parts[1:]
    if not errors and not briefs and not re.fullmatch(r"-?\s*`?None\.?`?", preamble.strip(), re.IGNORECASE):
        error("OWNER_FORM", "Waiting on owner must hold one '###' decision brief per decision, or 'None.'")

    for number, brief in enumerate(briefs, start=1):
        heading, _, rest = brief.partition("\n")
        label = f"brief {number}"
        if len(re.findall(r"\w", re.sub(r"^[0-9]+[.)]\s*", "", heading.strip()))) < 10:
            error("BRIEF_DECISION", f"{label} heading must state the decision in one sentence")
        if re.search(r"<[^<>\n]+>", brief):
            error("BRIEF_PLACEHOLDER", f"{label} still contains a <placeholder>")
        values: dict[str, str] = {}
        for key in BRIEF_KEYS:
            match = re.search(r"^\s*-\s*" + re.escape(key) + r"\s*:(.*)$", rest, re.IGNORECASE | re.MULTILINE)
            if not match:
                error("BRIEF_FIELD", f"{label} is missing '{key}'")
                continue
            values[key] = match.group(1).strip()
            if key != "Options" and len(re.findall(r"\w", values[key])) < 3:
                error("BRIEF_FIELD", f"{label} '{key}' is empty")
        if "What it is" in values and len(values["What it is"].split()) < 8:
            error("BRIEF_EXPLAIN", f"{label} 'What it is' must explain the subject, not name it")
        options_block = re.search(
            r"^\s*-\s*Options\s*:.*?$(.*?)(?=^\s*-\s*(?:" + "|".join(re.escape(k) for k in BRIEF_KEYS if k != "Options") + r")\s*:|\Z)",
            rest,
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        options = [line.strip() for line in (options_block.group(1) if options_block else "").splitlines()
                   if re.match(r"^\s+[-*]\s+\S", line)]
        if "Options" in values and len(options) < 2:
            error("BRIEF_OPTIONS", f"{label} needs at least two options, one per nested bullet")
        for option in options:
            for key in ("Cost", "Effect"):
                if not re.search(r"\b" + key + r"\s*:\s*\S", option, re.IGNORECASE):
                    error("BRIEF_OPTION_COST", f"{label} option '{option[:40]}' has no {key}:")
        introduced = values.get("What it is", "")
        for ident in sorted(set(match.group(0) for match in BRIEF_ID.finditer(brief))):
            if BRIEF_ID_ALLOWED.match(ident):
                continue
            if ident not in introduced:
                error("BRIEF_BARE_ID", f"{label} uses {ident} without introducing it in 'What it is'")

    if errors:
        for item in errors:
            print(f"ERROR {item}")
        print(f"orchestration lint: FAIL ({len(errors)} error(s))")
        return 1
    print(f"orchestration lint: PASS (handoff, {len(briefs)} decision brief(s))")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--handoff", type=Path, help="HANDOFF.md to check (phase handoff)")
    parser.add_argument("--phase", required=True, choices=("review", "dispatch", "docs", "handoff"))
    args = parser.parse_args()
    if args.phase == "handoff":
        if args.handoff is None:
            parser.error("--phase handoff requires --handoff")
        return lint_handoff(args.handoff.resolve())
    missing = [name for name in ("contract", "plan", "packet") if getattr(args, name) is None]
    if missing:
        parser.error(f"--phase {args.phase} requires " + ", ".join(f"--{name}" for name in missing))
    linter = Linter(args.contract.resolve(), args.plan.resolve(), args.packet.resolve(), args.phase)
    return linter.run()


if __name__ == "__main__":
    sys.exit(main())
