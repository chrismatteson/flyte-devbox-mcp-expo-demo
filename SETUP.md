# Booth Setup & Operations

Operator guide for running the **Stump the Agent** booth. For the pitch, the
booth loop, and the visitor prompt menu, see [README.md](README.md).

---

## One-time setup (do this before the expo)

1. **Open this folder in VS Code** with the Claude Code extension.
2. **Create the environment** (Python ≥ 3.10) — dependencies are pinned in
   `pyproject.toml`:
   ```bash
   uv sync
   # then use `uv run flyte ...`, or activate with `source .venv/bin/activate`
   ```
3. **Start the local Flyte devbox** (the k3s container that serves
   `localhost:30080`). Confirm it's up:
   ```bash
   flyte --config .flyte/config.yaml get project --project flytesnacks --domain development
   ```
4. **Open a browser tab** to `http://localhost:30080/v2/` on the screen the
   audience sees.

### Pre-flight checklist (morning of)
- [ ] Devbox container running; `get project` returns `flytesnacks`.
- [ ] Warm run succeeds end-to-end (see below) and the **Report** renders.
- [ ] **Reset Booth** button (status bar) archives cleanly with no terminal popup.
- [ ] `/clear` (Cmd+K twice) archives + resets without a hitch.
- [ ] Mic / dictation working in VS Code (macOS: press **Fn** twice to dictate).

### Smoke test
There are **no example files** — the booth builds everything on the spot. To warm
up, hand Claude any prompt from the menu in [README.md](README.md) (e.g. *"Run a
swarm of trader bots on a market for moon rubble and crown the richest"*). Claude
writes `tasks/<name>.py`, runs it on the devbox, and prints a
`localhost:30080/v2/...` URL. Open it → click **Report** → confirm the tabs
render. Re-run with a different `--seed` and confirm you get a different result.
Then `bash scripts/reset.sh` to clear before the floor opens.

---

## Running the booth

1. **Visitor speaks an idea.** If they're shy, offer the prompt menu in
   [README.md](README.md).
2. Claude builds `tasks/<name>.py` and runs it. **Read the run URL aloud / open
   it** on the audience screen.
3. Walk them through the **Report** — the traits, the parallel fan-out, the
   scoring. Let them see it's real.
4. **Reset:** click the **Reset Booth** button in the status bar (no keyboard
   needed). This does a full reset in one click — it starts a fresh Claude
   conversation **and** archives their work to `archive/<timestamp>/` (via the
   `SessionStart` hook), leaving `tasks/` clean for the next person. Pressing
   **Cmd+K twice** (`/clear`) does the same thing from the keyboard.

---

## Reset & archive

| Action | What it does |
|---|---|
| **Reset Booth** button (status bar) | Mouse-only, no keyboard. **Full reset:** starts a fresh conversation (runs `claude-vscode.newConversation`) **and** archives `tasks/*` → `archive/<timestamp>/` via the `SessionStart` `clear` hook. Silent — no terminal popup. |
| **Cmd+K twice** (`/clear`) | The keyboard equivalent — same fresh conversation + archive. |

Both paths run `scripts/reset.sh` (via the hook), which only ever **moves** files
into `archive/<timestamp>/` — nothing is deleted and git is never touched, so
every visitor's creation is preserved and you can revisit the best ones later.

---

## Troubleshooting
- **A run is slow / "Building image…" appears:** a non-stdlib dependency slipped
  in. Reset and re-prompt; Claude is instructed to stay stdlib-only.
- **`run not found` on `get run`:** pass `--project flytesnacks --domain development`.
- **Devbox unreachable:** confirm the container is up and `localhost:30080`
  responds; restart it if needed.
- **`flyte: command not found`:** activate the venv or use `.venv/bin/flyte`.
- **Map task errors with "coroutine":** that only happens with `--local`. Always
  run on the devbox (the command in `CLAUDE.md`).
