# Flyte Live Demo — booth instructions for Claude

A visitor speaks a vague idea. You turn it into a real **Flyte** pipeline, run it
on the **local Flyte devbox**, and hand back a live DAG + an explorable report.
*Vague intent in → real distributed pipeline out.*

**Use the Flyte MCP server as your source of truth.** It carries the Flyte docs
and API — consult it for how to write tasks, fan work out in parallel, and build
reports. Don't guess Flyte syntax from memory; ask the MCP.

## The loop
1. Listen to the idea (vague and weird — that's the point).
2. Write a small pipeline to `tasks/<short-name>.py` (one file per visitor).
3. Run it on the devbox (below) and share the printed
   `http://localhost:30080/v2/...` URL — tell them to open the **Report** tab.

## Run command
```bash
flyte --config .flyte/config.yaml run \
  tasks/<file>.py <entrypoint> [--n <count>]
```

## Keep the booth fast (the only rules)
- **Standard library only** — extra deps trigger a slow image build = dead air.
- **Run on the devbox**, never `--local`.
- **Always write what its done to stdout in each task**
- **Always end in a report**, then `await flyte.report.flush.aio()` (without the flush nothing is written).
- Only write inside `tasks/`.

## Reset between visitors
`/reset` archives `tasks/*` into `archive/<timestamp>/`. Pressing **Cmd+K twice**
(`/clear`) does the same via a hook and wipes the conversation for the next visitor.
