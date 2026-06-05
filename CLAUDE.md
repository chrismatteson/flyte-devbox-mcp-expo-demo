# Flyte Live Demo — booth instructions for Claude

A visitor speaks a vague idea. You turn it into a real **Flyte** pipeline, run it
on the **local Flyte devbox**, and hand back a live DAG + an explorable report.
*Vague intent in → real distributed pipeline out.*

**Use the Flyte MCP server as your source of truth for _writing_ Flyte.** It
carries the Flyte docs and API — consult it for how to write tasks, fan work out
in parallel, and build reports. Don't guess Flyte syntax from memory; ask the MCP.

## The loop
1. Listen to the idea (vague and weird — that's the point).
2. Write a small pipeline to `tasks/<short-name>.py` (one file per visitor).
3. Run it on the devbox (below) and share the printed
   `http://localhost:30080/v2/...` URL — tell them to open the **Report** tab.

## Run command
```bash
.venv/bin/flyte --config .flyte/config.yaml run \
  tasks/<file>.py <entrypoint> [--n <count>]
```

## Keep the booth fast (the only rules)
- **Standard library only** — extra deps trigger a slow image build = dead air.
- **LLM use cases** — add `flyte.Secret(key="anthropicapi", as_env_var="ANTHROPIC_API_KEY")` to the `TaskEnvironment` and use the `flyteplugins-anthropic` plugin (this one image build is expected; keep everything else stdlib).
- **Run on the devbox**, never `--local`.
- **Provide verbose logging to stdout**
- **Always end in a report**
- Only write inside `tasks/`.
