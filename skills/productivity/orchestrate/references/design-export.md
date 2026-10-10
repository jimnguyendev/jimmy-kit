# Exporting a claude.ai Design project before frontend dispatch

Read when frontend packets must follow a design that lives in claude.ai Design.

## Rule

The root exports the design pages into the target repo, commits them to the default branch,
and only then writes FE packets that point at the exported files by absolute path. Executors
never read the design service directly.

## Why

- DesignSync is effectively root-only. Subagents usually do not get the tool (one probe had it;
  the next nine subagents in the origin run did not), so an FE packet that says "read the design"
  produces a guess.
- A screenshot or canvas export is not a spec. The origin run's first FE wave was built from
  exported canvas images and the owner rejected it as unlike the design; the second wave was
  built from the exported page sources and verified page by page against them.

## Steps

1. In the root session, list the project's pages and call DesignSync `get_file` for every page
   and every asset a page imports. Do not summarize or retype the results.
2. Extract them byte for byte from the root's own transcript:

   ```bash
   python3 <installed-skill-dir>/scripts/extract-design.py <repo>/design/spec \
     ~/.claude/projects/<project-dir>/<session-id>.jsonl
   ```

   The script prints `path  bytes  truncated=` per file and never prints contents. Any
   `truncated=True` file is fetched again (smaller range or per asset) before going on.
3. Commit `design/spec/` to the default branch through the normal land path.
4. Write an FE brief that explains the export's format once (markup, logic blocks, where variant
   states are declared, how its components map to the repo's UI library), and in each FE packet
   name the spec files it implements and the states each must support.

## HTML exports with iframe artboards

When a design export is a single HTML file whose artboards are JS-rendered iframes, read each
artboard through its own CDP target (`Runtime.evaluate` of `document.documentElement.outerHTML`)
and screenshot the dumped HTML as a top-level tab. `file://` iframes are separate origins
(`contentDocument` is null), the page's frame tree is empty, and `Page.captureScreenshot` works
only on top-level targets.
