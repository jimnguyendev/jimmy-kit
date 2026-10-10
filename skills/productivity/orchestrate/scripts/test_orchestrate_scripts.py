#!/usr/bin/env python3
"""Black-box tests for the bundled land, gate, context-hook and design-export scripts.

Every test builds its own throwaway repositories under a temporary directory: a bare
`origin`, a main checkout cloned from it, and one packet worktree. The GitHub CLI is
replaced by a stub on PATH that records its calls and performs the merge on the bare
origin, so the land flow runs end to end without network access.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
GATES = SCRIPT_DIR / "gates.sh"
LAND = SCRIPT_DIR / "land.sh"
HOOK = SCRIPT_DIR / "orchestrate-context.sh"
EXTRACT = SCRIPT_DIR / "extract-design.py"

GH_STUB = textwrap.dedent(
    """\
    #!/usr/bin/env bash
    # Minimal gh stand-in: one PR (#7) whose merge fast-forwards the bare origin.
    echo "$*" >>"$STUB_LOG"
    case "$1 $2" in
      "pr list") echo "" ;;
      "pr create") echo "https://github.com/example/repo/pull/7" ;;
      "pr view")
        case "$*" in
          *mergeable*) echo MERGEABLE ;;
          *state*) if [ -f "$STUB_ORIGIN.merged" ]; then echo MERGED; else echo OPEN; fi ;;
        esac ;;
      "pr merge")
        [ -z "${STUB_MERGE_FAIL:-}" ] || { echo "merge refused" >&2; exit 1; }
        sha=""; prev=""
        for a in "$@"; do [ "$prev" = "--match-head-commit" ] && sha="$a"; prev="$a"; done
        [ -n "$sha" ] || { echo "no --match-head-commit" >&2; exit 1; }
        git -C "$STUB_ORIGIN" update-ref refs/heads/main "$sha"
        touch "$STUB_ORIGIN.merged" ;;
      *) echo "unexpected gh call: $*" >&2; exit 1 ;;
    esac
    """
)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class Repos:
    """origin (bare) · main checkout · packet worktree, plus a gate file and a gh stub."""

    def __init__(self, gates: str = "build: test -f feature.txt\n") -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orchestrate-scripts-")
        self.root = Path(os.path.realpath(self.tmp.name))
        self.origin = self.root / "origin.git"
        self.repo = self.root / "repo"
        self.wt = self.root / "repo-wt" / "001-feature"
        self.bin = self.root / "bin"
        self.log = self.root / "gh.log"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.repo)], check=True, capture_output=True)
        for key, value in (("user.email", "t@example.com"), ("user.name", "t"), ("commit.gpgsign", "false")):
            git(self.repo, "config", key, value)
        (self.repo / ".gitignore").write_text(".orchestrate/\n", encoding="utf-8")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")
        git(self.repo, "push", "-q", "origin", "main")
        git(self.repo, "remote", "set-head", "origin", "main")
        state = self.repo / ".orchestrate"
        state.mkdir()
        (state / "gates").write_text(gates, encoding="utf-8")
        git(self.repo, "worktree", "add", "-q", "-b", "p001-feature", str(self.wt), "main")
        (self.wt / "feature.txt").write_text("feature\n", encoding="utf-8")
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-q", "-m", "feature")
        self.bin.mkdir()
        stub = self.bin / "gh"
        stub.write_text(GH_STUB, encoding="utf-8")
        stub.chmod(0o755)

    def env(self, **extra: str) -> dict:
        env = dict(os.environ)
        env.update(
            {
                "PATH": f"{self.bin}{os.pathsep}{env['PATH']}",
                "STUB_LOG": str(self.log),
                "STUB_ORIGIN": str(self.origin),
                "ORCH_FORGE": "github",
                "ORCH_MERGE_WAIT": "6",
                "TMPDIR": str(self.root),
                "GIT_CONFIG_GLOBAL": str(self.root / "gitconfig"),
            }
        )
        env.update(extra)
        return env

    def run(self, *cmd: str, stdin: str | None = None, **extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            list(cmd), cwd=self.root, env=self.env(**extra), input=stdin,
            capture_output=True, text=True, check=False,
        )

    def origin_has_branch(self, name: str) -> bool:
        return bool(git(self.origin, "branch", "--list", name))

    def __enter__(self) -> "Repos":
        (self.root / "gitconfig").write_text(
            "[user]\n\temail = t@example.com\n\tname = t\n[commit]\n\tgpgsign = false\n", encoding="utf-8"
        )
        return self

    def __exit__(self, *_: object) -> None:
        self.tmp.cleanup()


class GatesTests(unittest.TestCase):
    def test_all_gates_pass(self) -> None:
        with Repos("build: test -f feature.txt\n# comment\n\nlint: true\n") as r:
            result = r.run("bash", str(GATES), str(r.wt))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ok   build", result.stdout)
            self.assertIn("gates: all 2 ok", result.stdout)

    def test_first_failure_stops_and_names_log(self) -> None:
        with Repos("build: true\ntest: echo boom; exit 3\nlater: touch ran-later\n") as r:
            result = r.run("bash", str(GATES), str(r.wt))
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL test", result.stdout)
            self.assertFalse((r.wt / "ran-later").exists())
            log = r.root / f"gates-{r.wt.name}" / "test.log"
            self.assertIn("boom", log.read_text(encoding="utf-8"))

    def test_missing_or_empty_gate_file_is_a_usage_error(self) -> None:
        with Repos("# nothing here\n") as r:
            self.assertEqual(r.run("bash", str(GATES), str(r.wt)).returncode, 2)
            missing = r.run("bash", str(GATES), str(r.wt), ORCH_GATES_FILE=str(r.root / "none"))
            self.assertEqual(missing.returncode, 2)

    def test_malformed_line_is_rejected(self) -> None:
        with Repos("just a command without a name\n") as r:
            self.assertEqual(r.run("bash", str(GATES), str(r.wt)).returncode, 2)


class LandTests(unittest.TestCase):
    def test_gate_failure_pushes_nothing_and_keeps_worktree(self) -> None:
        with Repos("build: exit 1\n") as r:
            result = r.run("bash", str(LAND), str(r.wt), "feature")
            self.assertEqual(result.returncode, 1)
            self.assertIn("gates failed; nothing was pushed", result.stderr)
            self.assertFalse(r.origin_has_branch("p001-feature"))
            self.assertTrue(r.wt.exists())
            self.assertFalse(r.log.exists(), "gh must not be called when a gate fails")

    def test_dirty_worktree_is_refused(self) -> None:
        with Repos() as r:
            (r.wt / "scratch.txt").write_text("x", encoding="utf-8")
            result = r.run("bash", str(LAND), str(r.wt), "feature")
            self.assertEqual(result.returncode, 1)
            self.assertIn("uncommitted or untracked", result.stderr)

    def test_main_checkout_is_refused(self) -> None:
        with Repos() as r:
            self.assertEqual(r.run("bash", str(LAND), str(r.repo), "feature").returncode, 1)

    def test_success_merges_with_head_sha_then_removes_worktree(self) -> None:
        with Repos() as r:
            # main moves on after the worktree was cut: land must merge it in before gating.
            (r.repo / "other.txt").write_text("other\n", encoding="utf-8")
            git(r.repo, "add", "other.txt")
            git(r.repo, "commit", "-q", "-m", "other")
            git(r.repo, "push", "-q", "origin", "main")
            result = r.run("bash", str(LAND), str(r.wt), "feature")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = r.log.read_text(encoding="utf-8")
            merged_head = git(r.origin, "rev-parse", "main")
            self.assertIn(f"--match-head-commit {merged_head}", calls)
            files = git(r.origin, "ls-tree", "--name-only", "main").split()
            self.assertIn("feature.txt", files)
            self.assertIn("other.txt", files)
            self.assertFalse(r.wt.exists())
            self.assertEqual(git(r.repo, "rev-parse", "HEAD"), merged_head)

    def test_refused_merge_keeps_worktree(self) -> None:
        with Repos() as r:
            result = r.run("bash", str(LAND), str(r.wt), "feature", STUB_MERGE_FAIL="1")
            self.assertEqual(result.returncode, 1)
            self.assertIn("worktree kept", result.stderr)
            self.assertTrue(r.wt.exists())


class ContextHookTests(unittest.TestCase):
    def setup_state(self, r: Repos) -> None:
        state = r.repo / ".orchestrate"
        (state / "SPRINT.md").write_text("# Sprint\n", encoding="utf-8")
        (state / "HANDOFF.md").write_text("# Handoff\nNext: land 001\n", encoding="utf-8")

    def test_snapshot_then_resume_in_target_repo(self) -> None:
        with Repos() as r:
            self.setup_state(r)
            stdin = json.dumps({"cwd": str(r.repo), "trigger": "auto"})
            snap = r.run("bash", str(HOOK), "snapshot", stdin=stdin)
            self.assertEqual(snap.returncode, 0, snap.stderr)
            auto = (r.repo / ".orchestrate" / "AUTO-STATE.md").read_text(encoding="utf-8")
            self.assertIn("trigger: auto", auto)
            self.assertIn("## main (last 12 commits)", auto)
            self.assertIn("[p001-feature] ahead=1", auto)
            resume = r.run("bash", str(HOOK), "resume", stdin=json.dumps({"cwd": str(r.repo), "source": "compact"}))
            self.assertIn("Next: land 001", resume.stdout)
            self.assertIn("AUTO-STATE.md", resume.stdout)

    def test_targets_file_maps_another_cwd(self) -> None:
        with Repos() as r:
            self.setup_state(r)
            other = r.root / "elsewhere"
            other.mkdir()
            targets = r.root / "targets"
            targets.write_text(f"{other} {r.repo}\n", encoding="utf-8")
            resume = r.run("bash", str(HOOK), "resume", stdin=json.dumps({"cwd": str(other)}), ORCH_TARGETS=str(targets))
            self.assertIn("Next: land 001", resume.stdout)

    def test_unrelated_session_is_silent(self) -> None:
        with Repos() as r:
            result = r.run("bash", str(HOOK), "resume", stdin=json.dumps({"cwd": str(r.root)}), ORCH_TARGETS=str(r.root / "none"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")


class ExtractDesignTests(unittest.TestCase):
    def transcript(self, root: Path, results: list[dict]) -> Path:
        path = root / "session.jsonl"
        lines = [json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": json.dumps(obj, separators=(",", ":"))}]}}) for obj in results]
        path.write_text("not json\n" + "\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_writes_text_and_base64_files_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png = bytes(range(256))
            t = self.transcript(root, [
                {"method": "get_file", "path": "pages/Main.html", "content": "<x-dc>é</x-dc>", "truncated": False},
                {"method": "get_file", "path": "img/logo.png", "content": base64.b64encode(png).decode(), "isBase64": True},
            ])
            out = root / "spec"
            result = subprocess.run(["python3", str(EXTRACT), str(out), str(t)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((out / "pages/Main.html").read_text(encoding="utf-8"), "<x-dc>é</x-dc>")
            self.assertEqual((out / "img/logo.png").read_bytes(), png)
            self.assertNotIn("<x-dc>", result.stdout)

    def test_path_escaping_out_dir_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            t = self.transcript(root, [{"method": "get_file", "path": "../evil.txt", "content": "x"}])
            result = subprocess.run(["python3", str(EXTRACT), str(root / "spec"), str(t)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse((root / "evil.txt").exists())

    def test_no_results_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            t = self.transcript(root, [])
            result = subprocess.run(["python3", str(EXTRACT), str(root / "spec"), str(t)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
