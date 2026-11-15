# Calculate Anything: guide for coding agents

An Alfred 5 workflow. Type a number in Alfred and it converts currency, crypto, units, data sizes, percentages, CSS sizes and inline VAT; the `time`, `vat` and `color` keywords do dates, VAT breakdowns and colors. Python, standard library only, rebuilt in 2026 from an archived PHP workflow.

This folder is the installed workflow inside the owner's Alfred preferences. Alfred runs these files directly, so every saved edit is live.

## Docs

Read the one that matches what you are about to do, and update it when you change what it describes.

- `docs/ARCHITECTURE.md`: before changing code. Request flow, module contracts, the rates cache, `info.plist` wiring, how to add a unit, currency, rate source, language or calculator.
- `docs/PRD.md`: before changing behaviour or scope. Requirements, non-goals, open questions, backlog.
- `docs/MEMORY.md`: before revisiting a decision, debugging an Alfred quirk, or testing inside Alfred. Decisions with their reasons, verified Alfred behaviour, the live-test procedure, environment facts, history.
- `docs/LOCAL.md`, on the owner's Mac only (git ignores it): before testing inside Alfred or touching anything outside this folder. Paths, backup setup, accounts, house rules.
- `docs/CHANGELOG.md`: release notes.
- `docs/MANUAL.md`: the user manual, every query form and setting. Update it with every change users can see.
- `README.md`: the landing page, with install steps and a quick tour.

## Rules

- Write for `/usr/bin/python3`, Apple's Python 3.9.6: 3.9 syntax, standard library only.
- Keep the keystroke path offline. Alfred runs `calculate.py` on every keystroke; network access lives only in the detached refresh in `ca/rates.py`.
- Every run prints valid Script Filter JSON on stdout; tracebacks go to stderr.
- At runtime, write only under `$alfred_workflow_data` and `$alfred_workflow_cache`. The folder itself stays exactly as shipped, with no `__pycache__`.
- Edit `info.plist` with `plistlib`, keep every object UID, then run `plutil -lint info.plist`. Alfred edits this file too, so always start from the copy on disk.
- `prefs.plist`, once Alfred writes it, holds the owner's saved settings and may hold API keys: leave it as Alfred wrote it. Git ignores it and packages leave it out.
- The `time` keyword stays `time`. The owner chose it on 2026-11-15 knowing DevToys uses it too.
- This folder is a public git repository: https://github.com/situmorang-com/alfred-calculate-anything. Everything tracked is public, so notes about the owner or their Mac go in `docs/LOCAL.md`.
- Commit messages are a summary line and a body, without `Co-Authored-By` trailers (the owner's rule). Push only when the owner asks.
- Record what you learn in `docs/MEMORY.md`, dated. It is the shared memory for every agent that works here, whichever tool you are.

## Change loop

1. Read the `docs/ARCHITECTURE.md` section for the area you touch.
2. Change the code, and add a test to `tests/test_calculate.py` that pins the new behaviour.
3. Run the suite with both interpreters. Done when both print `OK`:
   ```bash
   /usr/bin/python3 tests/test_calculate.py
   /opt/homebrew/bin/python3 tests/test_calculate.py
   ```
4. Run the query the way Alfred does: `/usr/bin/python3 calculate.py "100 usd to idr"`.
5. Update the docs the change touched: decisions and learnings in `docs/MEMORY.md`, scope in `docs/PRD.md`, structure in `docs/ARCHITECTURE.md`. For a release, add an entry to `docs/CHANGELOG.md` and bump `version` in `info.plist` and `__version__` in `ca/__init__.py`.
6. Test inside Alfred only by the procedure in `docs/MEMORY.md`, "Live testing in Alfred". It starts by asking the owner for hands-off time.
7. Commit. Done when `git status` shows a clean tree.

## Commands

Run from this folder.

| Task | Command |
| --- | --- |
| Tests | `/usr/bin/python3 tests/test_calculate.py` |
| A query typed with no keyword | `/usr/bin/python3 calculate.py "100 usd to idr"` |
| A keyword query | `/usr/bin/python3 calculate.py --time "+15 days"` (also `--vat`, `--color`) |
| What the `.` and `-` triggers send | `/usr/bin/python3 calculate.py --dot "5 km to m"`, `--neg "25f to c"` |
| Download rates now | `/usr/bin/python3 calculate.py --refresh` (or `--refresh currency`, `--refresh crypto`) |
| Delete cached rates | `/usr/bin/python3 calculate.py --clear` |
| Package | `zip -r -FS -X -q "../../../dist/Calculate Anything.alfredworkflow" . -x '*.DS_Store' -x '*__pycache__*' -x 'prefs.plist' -x '.git/*' -x '.gitignore' -x 'docs/LOCAL.md'` |
| Release (owner asks; version bumped, committed, pushed) | Package, copy it to a scratch folder as `Calculate.Anything.alfredworkflow`, then `gh release create v<version> <that file> --target main --title "Calculate Anything <version>" --notes-file <notes>` |

Command-line runs share Alfred's real cache in `~/Library/Application Support/Alfred/Workflow Data/com.situmorang.calculateanything/`. To experiment without touching it, point `alfred_workflow_data` at a scratch folder; the test suite does this itself.
