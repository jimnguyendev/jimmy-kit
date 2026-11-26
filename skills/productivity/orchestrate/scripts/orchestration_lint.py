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
# A plan or packet that mentions one of these changes semantics a weaker reviewer misses; its
# packet must carry an `advisor:` line. One constant, so the list is changed in one place.
RISK_WORDS = (
    "queue", "lease", "retry", "retries", "backoff", "lock", "fencing", "idempot",
    "rebalance", "offset", "outbound", "state machine",
)
RISK_PATTERN = re.compile(
    r"\b(?:" + "|".join(w.replace(" ", r"[\s-]+") for w in RISK_WORDS) + r")\w*", re.IGNORECASE
)
AUDIT_EVERY_DEFAULT = 6
# New tests one packet may add without a named waiver. Executors follow the packet over AGENTS.md,
# so a packet that lists cases is the only test budget that holds.
TEST_BUDGET = 3
# Wording that asks for a test per item instead of one test per risk.
TEST_PER_ITEM = re.compile(
    r"\b(?:every|each)\s+finding\b|\bone\s+(?:test|case|assertion)\s+per\s+\w+|\bper[\s-]+role\b"
    r"|\bfor\s+(?:every|each)\s+row\b",
    re.IGNORECASE,
)
# The layer a new test runs at. One risk is tested at one layer: a rule table at `unit` (Validate,
# pure decisions), one `route` row to prove the handler path, `acceptance` only for a seam (rows
# written, a request out, a real engine), `vitest` for SPA code.
TEST_LAYERS = ("unit", "route", "acceptance", "vitest")
AC_REF = re.compile(r"\bAC-[0-9]+\b", re.IGNORECASE)
# A Volume and budget line that reports a measured number (not a target) carries its limiter and runs:
# "Measured: p99 41 ms", "baseline 120 ms", "measured p95 = 80 ms"; not "measured by EXPLAIN ANALYZE"
# or "measured at 1x and 10x". Only a time or a rate counts; a row or byte count is AC-007's cost number.
MEASURED = re.compile(
    r"\b(?:measured|baseline)\b\s*(?:p[0-9]{2,3}\b\s*)?(?:[:=]|\bat\b|\bis\b|\bwas\b|\bof\b)?\s*"
    r"(?:p[0-9]{2,3}\b\s*)?[~\u2248]?[0-9][0-9.,]*\s*"
    r"(?:[n\u00b5u]?s\b|ms\b|sec|min|\w*/s\b|rps\b|qps\b)",
    re.IGNORECASE,
)
BRIEF_KEYS = ("What it is", "Why now", "Options", "Recommendation", "If no answer", "Evidence")
# Ids an owner may not know: ADR-0017, PR #12, MR !34, #123, !34, a ticket key such as ABC-42.
BRIEF_ID = re.compile(
    r"\bADR[- ]?[0-9]+\b|\b(?:PR|MR)\s*[#!]?[0-9]+\b|(?<![\w/])[#!][0-9]+\b|\b[A-Z][A-Z0-9]{1,9}-[0-9]+\b"
)
# Standard names that look like ticket keys but need no explanation.
BRIEF_ID_ALLOWED = re.compile(r"^(?:UTF|SHA|ISO|HTTP|TLS|UTC|GMT|MD|BASE)-?[0-9]+$", re.IGNORECASE)
# Scope: a packet names where its scope came from on one `scope:` line, and an inventory read from a
# reference's source decides every row (references/product-fit.md#reference-inventory).
SCOPE_LINE = re.compile(r"^\s*[-*]?\s*`?scope`?\s*:\s*(.*?)\s*$", re.IGNORECASE | re.MULTILINE)
DATE = r"(?:[0-9]{1,2}/[0-9]{1,2}(?:/[0-9]{4})?|[0-9]{4}-[0-9]{2}-[0-9]{2})"
SEP = r"\s*[\u2014\u2013:-]+\s*"
OWNER_WORDS = (
    r"owner\s+(?P<date>" + DATE + r")\s*[\u2014\u2013:-]*\s*[\"\u201c](?P<quote>[^\"\u201c\u201d]+)[\"\u201d]"
)
SCOPE_OWNER = re.compile(r"^" + OWNER_WORDS + r"$", re.IGNORECASE)
SCOPE_FIX = re.compile(r"^fix(?:\s+[\u2014\u2013:-]+|\s*[\u2014\u2013:])\s*(?P<reason>.*)$", re.IGNORECASE)
SCOPE_ROWS = re.compile(r"^`?(?P<path>[^`#\s][^`#]*?)`?\s*#(?P<ids>.+)$")
INVENTORY_STATUSES = ("HAVE", "PARTIAL", "MISSING", "N/A")
DECISION_BUILD = re.compile(r"^build\s+`?[^\s`]*[0-9][^\s`]*`?(?:\s.*)?$", re.IGNORECASE)
DECISION_OWNER = re.compile(r"^(?P<kind>drop|later)" + SEP + OWNER_WORDS + r"\s*$", re.IGNORECASE)
DECISION_ROOT_CUT = re.compile(r"^(?:drop|later)\b", re.IGNORECASE)
DECISION_PROPOSE = re.compile(r"^propose-(?P<kind>drop|later)" + SEP + r"(?P<reason>\S.*)$", re.IGNORECASE)
DECISION_NA = re.compile(r"^n/a" + SEP + r"(?P<reason>\S.*)$", re.IGNORECASE)
DECISION_KINDS = ("build", "drop", "later", "propose-drop", "propose-later", "n/a", "none", "root-cut", "invalid")
REFERENCE_HEADER = re.compile(r"^\s*[-*]?\s*`?reference`?\s*:\s*(?P<value>.*?)\s*$", re.IGNORECASE)
INVENTORY_LINE = re.compile(r"^\W*inventory\s*:\s*`?([^`\s]+)`?\s*$", re.IGNORECASE | re.MULTILINE)


def letters(text: str) -> int:
    """Letters in any script, so a reason written in the owner's language counts the same."""
    return len(re.findall(r"[^\W\d_]", text))


def id_list(ids: list[str]) -> str:
    shown = ", ".join(ids[:10])
    return shown + (f" +{len(ids) - 10} more" if len(ids) > 10 else "")


def without_code(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return re.sub(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)


def find_near(value: str, near: Path | None) -> Path | None:
    """A path named inside a packet, sprint or handoff: relative to cwd, to the file, or to any parent of it."""
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None
    start = None if near is None else (near if near.is_dir() else near.parent)
    bases = [Path.cwd()] + ([start, *start.parents] if start else [])
    for base in bases:
        if (base / candidate).is_file():
            return base / candidate
    return None


def decision_kind(decision: str) -> str:
    """The kind of an inventory decision cell; one of DECISION_KINDS."""
    text = decision.strip()
    if not text:
        return "none"
    if DECISION_BUILD.match(text):
        return "build"
    owner = DECISION_OWNER.match(text)
    if owner and len(re.findall(r"\w", owner.group("quote"))) >= 3:
        return owner.group("kind").lower()
    if DECISION_ROOT_CUT.match(text):
        return "root-cut"
    proposed = DECISION_PROPOSE.match(text)
    if proposed and letters(proposed.group("reason")) >= 10:
        return "propose-" + proposed.group("kind").lower()
    reason = DECISION_NA.match(text)
    if reason and letters(reason.group("reason")) >= 10:
        return "n/a"
    return "invalid"


class Inventory:
    """One reference inventory file: its `reference:` header lines and the rows of every table that has
    `id`, `status` and `decision` columns (matched by header name, case-insensitive, any order)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.read_error = ""
        self.references: list[tuple[str, int]] = []
        self.tables = 0
        self.rows: list[dict[str, str]] = []
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            self.read_error = str(exc)
            return
        lines = without_code(text).splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            header = REFERENCE_HEADER.match(line)
            if header and not line.lstrip().startswith("|"):
                self.references.append((header.group("value"), index + 1))
            if line.lstrip().startswith("|") and index + 1 < len(lines) and self.is_separator(lines[index + 1]):
                columns = [self.cell(c).lower() for c in self.cells(line)]
                index += 2
                body: list[tuple[int, list[str]]] = []
                while index < len(lines) and lines[index].lstrip().startswith("|"):
                    body.append((index + 1, self.cells(lines[index])))
                    index += 1
                if all(name in columns for name in ("id", "status", "decision")):
                    self.tables += 1
                    for number, cells in body:
                        row = {name: self.cell(cells[at]) if at < len(cells) else "" for at, name in enumerate(columns)}
                        row["line"] = str(number)
                        self.rows.append(row)
                continue
            index += 1

    @staticmethod
    def cells(line: str) -> list[str]:
        parts = re.split(r"(?<!\\)\|", line.strip())
        if parts and not parts[0].strip():
            parts = parts[1:]
        if parts and not parts[-1].strip():
            parts = parts[:-1]
        return [part.strip().replace("\\|", "|") for part in parts]

    @staticmethod
    def cell(text: str) -> str:
        return re.sub(r"^[`*]+|[`*]+$", "", text.strip()).strip()

    def is_separator(self, line: str) -> bool:
        cells = self.cells(line)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    def proposed(self) -> list[dict[str, str]]:
        """Rows the root proposes to drop or defer; they wait on the owner."""
        return [
            row for row in self.rows
            if row.get("status") in ("PARTIAL", "MISSING") and decision_kind(row.get("decision", "")).startswith("propose-")
        ]


class Linter:
    def __init__(
        self,
        contract_path: Path | None,
        plan_path: Path | None,
        packet_path: Path | None,
        phase: str,
        sprint_path: Path | None = None,
        config_path: Path | None = None,
    ) -> None:
        self.contract_path = contract_path
        self.plan_path = plan_path
        self.packet_path = packet_path
        self.sprint_path = sprint_path
        self.config_path = config_path
        self.phase = phase
        self.config: dict[str, Any] = {}
        self.config_file: Path = Path.cwd() / ".claude" / "orchestrator.json"
        self.errors: list[str] = []
        self.contract: dict[str, Any] = {}
        self.plan = ""
        self.packet = ""
        self.inventory_paths: list[tuple[str, Path]] = []

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
        for line in lines:
            if not MEASURED.search(line):
                continue
            limiter = re.search(r"\blimiter\s*:\s*([^<\n—|;]*)", line, re.IGNORECASE)
            runs = re.search(r"\bruns\s*:\s*([^<\n—|;]*)", line, re.IGNORECASE)
            if (
                not limiter
                or len(re.findall(r"[A-Za-z]", limiter.group(1))) < 3
                or not runs
                or not re.search(r"[0-9]", runs.group(1))
            ):
                self.error(
                    "VOLUME_BUDGET",
                    f"`{line[:80]}` reports a measured number without `runs: <count, median and range>` and "
                    "`limiter: <the resource or code path that bounded it, from a profile or counters taken "
                    "during the run>`; a number without them is not evidence",
                )

    def validate_tests(self) -> None:
        """A packet lists every new test with its layer and the risk it guards, within a budget, never one per item."""
        packet = re.sub(r"<!--.*?-->", "", self.packet, flags=re.DOTALL)
        body = self.section(packet, "Tests")
        if body is None:
            self.error(
                "TESTS_SECTION",
                "packet has no `## Tests` section; add one line per new test "
                "(`- new: <layer>: <test> — guards: <behaviour that breaks silently without it>`) or `- none — <reason>`",
            )
        else:
            lines = [line.strip() for line in body.splitlines() if line.strip()]
            new = [line for line in lines if re.match(r"^-\s*new\s*:", line, re.IGNORECASE)]
            none = [line for line in lines if re.match(r"^-\s*`?none\b", line, re.IGNORECASE)]
            if not new and not none:
                self.error("TESTS_SECTION", "`## Tests` lists no `- new:` line and no `- none — <reason>`")
            elif new and none:
                self.error("TESTS_SECTION", "`## Tests` has both `- none` and `- new:` lines; keep one")
            elif none:
                reason = re.sub(r"^-\s*`?none`?\s*[:\-—–]*", "", none[0], flags=re.IGNORECASE)
                if len(re.findall(r"[A-Za-z]", reason)) < 10:
                    self.error("TESTS_SECTION", "`- none` needs a reason (10+ letters)")
            seen: dict[str, tuple[str, str]] = {}
            for line in new:
                match = re.match(r"^-\s*new\s*:\s*(.*?)\s*[—–;,-]*\s*guards\s*:\s*(.*)$", line, re.IGNORECASE)
                name, risk = (match.group(1), match.group(2)) if match else ("", "")
                if (
                    not match
                    or re.search(r"<[^<>]+>", line)
                    or len(re.findall(r"\w", name)) < 3
                    or len(re.findall(r"[A-Za-z]", risk)) < 10
                ):
                    self.error(
                        "TEST_RISK",
                        f"`{line[:80]}` needs a test name and `guards: <the behaviour that breaks silently "
                        "without it>`; a test that guards nothing named is not added",
                    )
                    continue
                layer_match = re.match(r"^(\w+)\s*:\s*\S", name)
                layer = layer_match.group(1).lower() if layer_match else ""
                if layer not in TEST_LAYERS:
                    self.error(
                        "TEST_LAYER",
                        f"`{line[:80]}` names no layer; start the test with `unit:` (a rule table: Validate, a pure "
                        "decision), `route:` (one row proving the handler path), `acceptance:` (a seam: rows written, "
                        "a request out, a real engine) or `vitest:`",
                    )
                key = re.sub(r"\W+", " ", re.split(r";\s*fails\s+if\b", risk, flags=re.IGNORECASE)[0].lower()).strip()
                owners = [key] + [ac.upper() for ac in AC_REF.findall(risk)]
                for owner in owners:
                    if owner not in seen:
                        continue
                    other_name, other_layer = seen[owner]
                    if layer and other_layer and layer != other_layer:
                        what = owner if owner.startswith("AC-") else "the same risk"
                        self.error(
                            "TEST_LAYER",
                            f"`{name}` ({layer}) and `{other_name}` ({other_layer}) both guard {what}; test it once, "
                            "at one layer: the rule table at unit, one route row for the handler path, acceptance "
                            "only for the seam",
                        )
                        break
                    if owner == key:
                        self.error(
                            "TEST_RISK", f"`{name}` guards the same risk as `{other_name}`; keep one test per risk"
                        )
                        break
                for owner in owners:
                    seen.setdefault(owner, (name, layer))
            waived = re.search(
                r"^\W*test\s+budget\s*:\s*waived\s+by\s+(\S.*?)\s*[—–:-]+\s*(\S.*)$",
                body,
                re.IGNORECASE | re.MULTILINE,
            )
            waiver_ok = waived is not None and len(re.findall(r"[A-Za-z]", waived.group(2))) >= 10
            if len(new) > TEST_BUDGET and not waiver_ok:
                self.error(
                    "TEST_BUDGET",
                    f"{len(new)} new tests (budget {TEST_BUDGET}); merge tests that guard one rule, leave copy and "
                    "layout to the root's walk, or add `test budget: waived by <who> — <reason>`",
                )

        current = ""
        for line in packet.splitlines():
            heading = re.match(r"^##\s+(.*?)\s*$", line)
            if heading:
                current = heading.group(1).lower()
                continue
            in_scope = current.startswith(("acceptance", "tests")) or re.search(r"\bAC-[0-9]+", line)
            hit = TEST_PER_ITEM.search(line) if in_scope else None
            if hit:
                self.error(
                    "TEST_PER_ITEM",
                    f"`{hit.group(0)}` asks for a test per item: `{line.strip()[:80]}`; name the risk once and "
                    "test the rule at its owner; copy and per-role screens go to the root's walk",
                )

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

    @staticmethod
    def ancestors(path: Path) -> list[Path]:
        start = path if path.is_dir() else path.parent
        return [start, *start.parents]

    def find_file(self, value: str, near: Path | None) -> Path | None:
        return find_near(value, near)

    def load_config(self) -> None:
        """`.claude/orchestrator.json`: --config, else the nearest one above the packet or sprint file."""
        path = self.config_path
        if path is None:
            for anchor in (self.packet_path, self.sprint_path, *(path for _, path in self.inventory_paths)):
                if anchor is None:
                    continue
                for base in self.ancestors(anchor):
                    if (base / ".claude" / "orchestrator.json").is_file():
                        path = base / ".claude" / "orchestrator.json"
                        break
                if path:
                    break
        if path is None:
            return
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.error("CONFIG_READ", f"cannot read {path}: {exc}")
            return
        if isinstance(parsed, dict):
            self.config = parsed
            self.config_file = path

    def reference_clones(self) -> dict[str, tuple[str, Path]]:
        """The config's `references`, keyed by lower-case name: (name, resolved clone path)."""
        references = self.config.get("references")
        if not isinstance(references, dict):
            return {}
        root = self.config_file.parent.parent if self.config_file.parent.name == ".claude" else self.config_file.parent
        clones: dict[str, tuple[str, Path]] = {}
        for name, location in references.items():
            if not isinstance(name, str) or not name or not isinstance(location, str):
                continue
            clone = Path(location).expanduser()
            clones[name.lower()] = (name, (clone if clone.is_absolute() else root / clone).resolve())
        return clones

    def validate_references(self) -> None:
        """A line that names a configured reference product must cite a file of its clone, or say why not."""
        clones = self.reference_clones()
        if not clones:
            return
        text = re.sub(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", "", self.packet, flags=re.MULTILINE | re.DOTALL)
        for name, clone in clones.values():
            word = re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)", re.IGNORECASE)
            for number, line in enumerate(text.splitlines(), start=1):
                if not word.search(line):
                    continue
                scope = SCOPE_LINE.fullmatch(line)
                if scope and SCOPE_ROWS.match(scope.group(1)) and not SCOPE_OWNER.match(scope.group(1)):
                    continue
                fix = (
                    f"cite the reference's code with `ref: <path in {name}'s clone>[:line]` on the line, "
                    "or write `ref: none — <reason>`; never list behaviour of a reference from memory"
                )
                cited = re.search(r"(?<!\w)ref\s*:\s*`?([^\s`]+)`?(.*)$", line, re.IGNORECASE)
                where = f"packet line {number} names reference '{name}'"
                if not cited:
                    self.error("REFERENCE_CITED", f"{where} without a citation; {fix}")
                    continue
                target, rest = cited.group(1), cited.group(2)
                if target.lower() == "none":
                    if not re.match(r"^\s*[\u2014\u2013-]+\s*\S", rest):
                        self.error("REFERENCE_CITED", f"{where} with `ref: none` and no reason; write `ref: none — <reason>`")
                    continue
                target = re.sub(r":[0-9]+(?:-[0-9]+)?$", "", target.rstrip(".,;)"))
                path = Path(target).expanduser()
                path = (path if path.is_absolute() else clone / path).resolve()
                if clone != path and clone not in path.parents:
                    self.error("REFERENCE_CITED", f"{where}; `ref: {target}` is outside {clone}")
                elif not path.exists():
                    self.error("REFERENCE_CITED", f"{where}; `ref: {target}` does not exist in {clone}; {fix}")

    def validate_scope(self) -> None:
        """The packet names where its scope came from: inventory rows it builds, the owner's words, or a fix."""
        hint = (
            "write one `scope:` line: `scope: <inventory path>#<id>[, <id>...]` (the inventory rows this packet "
            "builds), `scope: owner <date> — \"<the owner's words>\"` (the owner asked for exactly this), or "
            "`scope: fix — <the landed behaviour or audit finding it fixes>`"
        )
        match = SCOPE_LINE.search(without_code(self.packet))
        if not match:
            self.error("SCOPE_SOURCE", f"the packet has no `scope:` line; {hint}")
            return
        value = match.group(1)
        if re.search(r"<[^<>\n]+>", value):
            self.error("SCOPE_SOURCE", f"`scope: {value}` still holds a <placeholder>; {hint}")
            return
        owner = SCOPE_OWNER.match(value)
        if owner:
            if len(re.findall(r"\w", owner.group("quote"))) < 3:
                self.error("SCOPE_SOURCE", f"`scope: {value}` quotes no words of the owner; {hint}")
            return
        fix = SCOPE_FIX.match(value)
        if fix:
            if letters(fix.group("reason")) < 10:
                self.error("SCOPE_SOURCE", f"`scope: {value}` needs what it fixes (10+ letters); {hint}")
            return
        rows = SCOPE_ROWS.match(value)
        if not rows:
            self.error("SCOPE_SOURCE", f"`scope: {value}` is none of the three forms; {hint}")
            return
        label = rows.group("path").strip()
        ids = [ident for ident in (Inventory.cell(part).lstrip("#") for part in re.split(r"[,\s]+", rows.group("ids"))) if ident]
        if not ids:
            self.error("SCOPE_SOURCE", f"`scope: {value}` cites no inventory id; {hint}")
            return
        path = self.find_file(label, self.packet_path)
        if path is None:
            self.error("SCOPE_INVENTORY", f"inventory {label} named on the scope line does not exist; write it "
                       "(references/product-fit.md#reference-inventory) or fix the path")
            return
        inventory = Inventory(path)
        self.check_inventory(inventory, label)
        by_id = {row.get("id", ""): row for row in inventory.rows}
        missing = [ident for ident in ids if ident not in by_id]
        if missing:
            self.error("SCOPE_INVENTORY", f"scope cites {id_list(missing)}, not an id of {label}")
        not_built = [ident for ident in ids if ident in by_id and decision_kind(by_id[ident].get("decision", "")) != "build"]
        if not_built:
            self.error("SCOPE_INVENTORY", f"scope cites {id_list(not_built)} of {label}, whose decision is not "
                       "`build <packet id>`; set the row's decision to this packet before dispatching it")

    def check_inventory(self, inventory: Inventory, label: str) -> None:
        """The inventory rules of references/product-fit.md#reference-inventory, without any packet."""
        if inventory.read_error:
            self.error("SCOPE_INVENTORY", f"cannot read inventory {label}: {inventory.read_error}")
            return
        if not inventory.tables:
            self.error("SCOPE_INVENTORY", f"{label} has no table with `id`, `status` and `decision` columns; use "
                       "`| id | reference feature | ref | ours | status | decision |`")
        if not inventory.references:
            self.error("SCOPE_INVENTORY", f"{label} has no `reference: <name> @ <commit>` line; read the inventory from "
                       "the reference's source clone and name the commit read")
        clones = self.reference_clones()
        for value, number in inventory.references:
            header = re.match(r"^`?(?P<name>[^@`]+?)`?\s*@\s*`?(?P<commit>[^`\s]+)`?$", value)
            if not header:
                self.error("SCOPE_INVENTORY", f"{label} line {number}: `reference: {value}` must read "
                           "`reference: <name> @ <commit>`")
                continue
            name = header.group("name").strip()
            if name.lower() not in clones:
                self.error("SCOPE_INVENTORY", f"{label}: reference '{name}' is not a key of `references` in "
                           f".claude/orchestrator.json; add `\"{name}\": \"<clone path>\"` so the inventory and "
                           "REFERENCE_CITED read the same clone")
            elif not clones[name.lower()][1].exists():
                self.error("SCOPE_INVENTORY", f"{label}: the clone of reference '{name}' ({clones[name.lower()][1]}) "
                           f"does not exist; clone it at {header.group('commit')}")
        seen: set[str] = set()
        repeated: list[str] = []
        unnamed: list[str] = []
        bad_status: list[str] = []
        empty_ours: list[str] = []
        undecided: list[str] = []
        root_cut: list[str] = []
        for row in inventory.rows:
            ident = row.get("id", "")
            if not ident:
                unnamed.append(f"line {row['line']}")
                continue
            if ident in seen and ident not in repeated:
                repeated.append(ident)
            seen.add(ident)
            status = row.get("status", "")
            kind = decision_kind(row.get("decision", ""))
            if status not in INVENTORY_STATUSES:
                bad_status.append(ident)
            elif status == "HAVE":
                if not row.get("ours", ""):
                    empty_ours.append(ident)
            elif kind == "root-cut":
                root_cut.append(ident)
            elif status == "N/A" and kind != "n/a":
                undecided.append(ident)
            elif status in ("PARTIAL", "MISSING") and kind not in ("build", "drop", "later", "propose-drop", "propose-later"):
                undecided.append(ident)
        for items, message in (
            (unnamed, "rows without an id"),
            (repeated, "repeats ids"),
            (bad_status, "has a status other than HAVE, PARTIAL, MISSING or N/A on"),
            (empty_ours, "marks HAVE with an empty `ours` (name what we have, or the row is PARTIAL or MISSING) on"),
        ):
            if items:
                self.error("SCOPE_INVENTORY", f"{label} {message}: {id_list(items)}")
        if undecided:
            self.error("SCOPE_UNDECIDED", f"{label} rows {id_list(undecided)} have no valid decision; a PARTIAL or MISSING "
                       "row takes `build <packet id>`, `propose-drop — <reason>`, `propose-later — <reason>`, or "
                       "`drop` / `later — owner <date>: \"<quote>\"`; an N/A row takes `n/a — <reason>`")
        if root_cut:
            self.error("SCOPE_ROOT_DROP", f"{label} rows {id_list(root_cut)} are dropped or deferred without the owner's "
                       "words; write `propose-drop — <reason>` (or `propose-later`) and ask, then "
                       "`drop — owner <date>: \"<quote>\"` once the owner answers")

    def run_scope(self) -> int:
        """`--phase scope`: check each inventory and print its counts and strike list for the owner's report."""
        self.load_config()
        for label, path in self.inventory_paths:
            inventory = Inventory(path)
            self.check_inventory(inventory, label)
            statuses = [row.get("status", "") for row in inventory.rows]
            kinds = [decision_kind(row.get("decision", "")) for row in inventory.rows]
            print(f"inventory: {label}")
            print("  references: " + (", ".join(value for value, _ in inventory.references) or "none"))
            status_counts = [f"{name} {statuses.count(name)}" for name in INVENTORY_STATUSES]
            other = len([s for s in statuses if s not in INVENTORY_STATUSES])
            print("  status: " + " · ".join(status_counts + ([f"other {other}"] if other else [])))
            print("  decision: " + (" · ".join(f"{k} {kinds.count(k)}" for k in DECISION_KINDS if kinds.count(k)) or "none"))
            proposed = inventory.proposed()
            if not proposed:
                print("  strike list: none")
                continue
            rows_word = "row" if len(proposed) == 1 else "rows"
            print(f"  strike list ({len(proposed)} {rows_word} the root proposes to cut; the owner answers by id):")
            for kind in ("propose-drop", "propose-later"):
                rows = [row for row in proposed if decision_kind(row["decision"]) == kind]
                if not rows:
                    continue
                print(f"    {kind.replace('-', ' ')}:")
                for row in rows:
                    reason = DECISION_PROPOSE.match(row["decision"]).group("reason")  # type: ignore[union-attr]
                    print(f"    - {row['id']} · {row.get('reference feature', '')} · {reason}")
        return self.finish()

    def validate_advisor(self) -> None:
        """A plan or packet in the risk vocabulary needs an approved Advisor round or a named waiver."""
        text = self.packet + "\n" + self.plan
        hits = sorted({m.group(0).lower() for m in RISK_PATTERN.finditer(text)})
        if not hits:
            return
        value = self.field(r"^\s*-?\s*advisor\s*:\s*(.+)$", self.packet)
        how = (
            "run `<installed-skill-dir>/scripts/advisor-review.sh <plan.md>`, then add "
            "`advisor: PLAN_APPROVED <review file>` to the packet, or "
            "`advisor: waived by <who> — <reason>`"
        )
        if not value:
            self.error("ADVISOR_REQUIRED", f"the packet touches {', '.join(hits)} but has no `advisor:` line; {how}")
            return
        waived = re.match(r"^waived\s+by\s+(\S.*?)\s*[—:-]+\s*(\S.*)$", value, re.IGNORECASE)
        if waived:
            if len(re.findall(r"[A-Za-z]", waived.group(2))) < 10:
                self.error("ADVISOR_REQUIRED", "advisor waiver needs a reason (10+ letters)")
            return
        approved = re.match(r"^`?PLAN_APPROVED`?\s+`?([^`\s]+)`?", value)
        if not approved:
            self.error("ADVISOR_REQUIRED", f"`advisor: {value}` is not an approved verdict; {how}")
        elif self.find_file(approved.group(1), self.packet_path) is None:
            self.error("ADVISOR_REQUIRED", f"advisor review file {approved.group(1)} does not exist; {how}")

    def validate_executor(self) -> None:
        """The packet names its executor; the project may forbid some models (the root's own, for one)."""
        value = self.field(r"^\s*-?\s*executor\s*:\s*`?([^`\n]+?)`?\s*$", self.packet)
        if not value:
            self.error("EXECUTOR_FORBIDDEN", "the packet has no `executor: <model>` line; the root reads the seat from the packet")
            return
        forbidden = self.config.get("forbidden_executor_models", [])
        if isinstance(forbidden, list):
            tokens = set(re.split(r"[\s/:,@-]+", value.lower()))
            for model in forbidden:
                if isinstance(model, str) and model.lower() in tokens:
                    self.error(
                        "EXECUTOR_FORBIDDEN",
                        f"executor {value!r} is forbidden by forbidden_executor_models in .claude/orchestrator.json; "
                        "pick the model from executor_models for this packet kind",
                    )

    def validate_wave_audit(self) -> None:
        """More than `audit_every` packets landed since the last recorded audit stops the next dispatch."""
        assert self.sprint_path is not None
        try:
            lines = self.sprint_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            self.error("SPRINT_READ", f"cannot read sprint file: {exc}")
            return
        landed = 0
        for line in lines:
            audit = re.match(r"^\W*audit\s*:\s*`?([^`\s]+)`?\s*$", line, re.IGNORECASE)
            if audit:
                if self.find_file(audit.group(1), self.sprint_path) is not None:
                    landed = 0
                continue
            cells = [c.strip() for c in re.split(r"[|·]", line) if c.strip()]
            if len(cells) >= 3 and re.fullmatch(r"[0-9]+[a-z]?", cells[0]) and cells[2].strip("` *").lower() == "landed":
                landed += 1
        every = self.config.get("audit_every", AUDIT_EVERY_DEFAULT)
        if not isinstance(every, int) or every < 1:
            every = AUDIT_EVERY_DEFAULT
        if landed > every:
            self.error(
                "AUDIT_DUE",
                f"{landed} packets landed since the last audit (limit {every}); run the health pass "
                "(references/rules-and-enforcers.md#health-pass-after-a-wave) and record `audit: <path to the report>` in SPRINT.md",
            )

    def validate_dispatch_packet(self) -> None:
        """Rules that read the packet alone; they also run without a contract."""
        if self.packet_path is not None:
            self.validate_scope()
            self.validate_volume_budget()
            self.validate_references()
            self.validate_advisor()
            self.validate_executor()
            self.validate_tests()
        if self.sprint_path is not None:
            self.validate_wave_audit()

    def finish(self) -> int:
        if self.errors:
            for error in self.errors:
                print(f"ERROR {error}")
            print(f"orchestration lint: FAIL ({len(self.errors)} error(s))")
            return 1
        print(f"orchestration lint: PASS ({self.phase})")
        return 0

    def run_packet_only(self) -> int:
        """`--phase dispatch` without a contract: the packet-only rules."""
        self.load_config()
        for label, path in (("plan", self.plan_path), ("packet", self.packet_path)):
            if path is None:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                self.error("FILE_READ", f"cannot read {label} file: {exc}")
                text = ""
            if label == "plan":
                self.plan = text
            else:
                self.packet = text
        self.validate_dispatch_packet()
        return self.finish()

    def run(self) -> int:
        self.load_config()
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
        if self.phase == "review":
            self.validate_scope()
            self.validate_volume_budget()
            self.validate_references()
        if self.phase == "dispatch":
            self.validate_dispatch_packet()
            plan_status = self.field(r"^\s*-\s*Status:\s*`?([^`\s]+)", self.plan)
            if (plan_status or "").upper() != "APPROVED":
                self.error("PLAN_APPROVAL", "dispatch requires plan Status: APPROVED")
            packet_status = self.field(r"^\s*-\s*Approval state:\s*`?([^`\s]+)", self.packet)
            if (packet_status or "").upper() != "APPROVED":
                self.error("PACKET_APPROVAL", "dispatch requires packet Approval state: APPROVED")
        if self.phase == "docs":
            self.validate_docs()

        return self.finish()


def lint_handoff(path: Path, sprint: Path | None = None) -> int:
    """Check the `Waiting on owner` section of a HANDOFF file against the decision brief form.

    The form is defined by skill `ketchup` (references/decision-brief.md): one `###` per decision,
    keys in English, every key filled, at least two options with Cost and Effect, and every id used
    in a brief introduced in its `What it is` line. `None.` means nothing waits.

    Every inventory named on an `inventory:` line of SPRINT.md (`--sprint`, else the SPRINT.md next to
    the handoff) that still has `propose-*` rows must be named in `Waiting on owner`.
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
    is_none = re.fullmatch(r"-?\s*`?None\.?`?", preamble.strip(), re.IGNORECASE) is not None
    if not errors and not briefs and not is_none:
        error("OWNER_FORM", "Waiting on owner must hold one '###' decision brief per decision, or 'None.'")
    if briefs and is_none:
        error("OWNER_FORM", "Waiting on owner says 'None.' and also holds a brief; keep one")
    elif briefs and preamble.strip():
        error("OWNER_FORM", "Waiting on owner has text outside its '###' briefs; every question needs its own brief")

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
        # Language-neutral: count non-whitespace characters, not space-separated words, so an
        # explanation in a language written without spaces is measured the same way.
        if "What it is" in values and len(re.sub(r"\s", "", values["What it is"])) < 30:
            error("BRIEF_EXPLAIN", f"{label} 'What it is' must explain the subject (30+ characters), not name it")
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

    if sprint is None and (path.parent / "SPRINT.md").is_file():
        sprint = path.parent / "SPRINT.md"
    if sprint is not None:
        try:
            sprint_text = sprint.read_text(encoding="utf-8")
        except OSError as exc:
            error("SPRINT_READ", f"cannot read sprint file: {exc}")
            sprint_text = ""
        for named in INVENTORY_LINE.findall(sprint_text):
            found = find_near(named, sprint)
            if found is None:
                error("SCOPE_INVENTORY", f"SPRINT.md names inventory {named}, which does not exist")
                continue
            pending = [row["id"] for row in Inventory(found).proposed()]
            if pending and named not in body and found.name not in body:
                error(
                    "SCOPE_PENDING_OWNER",
                    f"{named} has rows the root proposes to drop or defer ({id_list(pending)}) and 'Waiting on owner' "
                    f"does not name it; add one brief \"which of these rows do we drop?\" whose 'What it is' names "
                    f"{named} and carries the strike list of `--phase scope`",
                )

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
    parser.add_argument("--sprint", type=Path, help="SPRINT.md: with --phase dispatch, fail AUDIT_DUE when too many packets landed since the last audit; with --phase handoff, the SPRINT.md whose inventory: lines are checked (default: next to the handoff)")
    parser.add_argument("--inventory", type=Path, nargs="+", help="reference inventory files to check and summarise (phase scope)")
    parser.add_argument("--config", type=Path, help=".claude/orchestrator.json (default: the nearest one above the packet or sprint file)")
    parser.add_argument("--phase", required=True, choices=("review", "dispatch", "docs", "handoff", "scope"))
    args = parser.parse_args()

    def resolve(path: Path | None) -> Path | None:
        return path.resolve() if path is not None else None

    if args.phase == "handoff":
        if args.handoff is None:
            parser.error("--phase handoff requires --handoff")
        return lint_handoff(args.handoff.resolve(), resolve(args.sprint))
    if args.phase == "scope":
        if not args.inventory:
            parser.error("--phase scope requires --inventory <file> [<file> ...]")
        linter = Linter(None, None, None, "scope", None, resolve(args.config))
        linter.inventory_paths = [(str(path), path.resolve()) for path in args.inventory]
        return linter.run_scope()

    if args.phase == "dispatch" and args.contract is None:
        if args.packet is None and args.sprint is None:
            parser.error("--phase dispatch without --contract requires --packet (and/or --sprint)")
        return Linter(None, resolve(args.plan), resolve(args.packet), "dispatch",
                      resolve(args.sprint), resolve(args.config)).run_packet_only()
    missing = [name for name in ("contract", "plan", "packet") if getattr(args, name) is None]
    if missing:
        parser.error(f"--phase {args.phase} requires " + ", ".join(f"--{name}" for name in missing))
    linter = Linter(args.contract.resolve(), args.plan.resolve(), args.packet.resolve(), args.phase,
                    resolve(args.sprint), resolve(args.config))
    return linter.run()


if __name__ == "__main__":
    sys.exit(main())
