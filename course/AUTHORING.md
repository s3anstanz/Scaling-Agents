# Authoring guide: Scaling Agents: From One to One Hundred

A standalone, hands-on interactive course that teaches how to build agents and teams of agents in Claude Code, from a single agent up to 100. Novice to expert. 20 lessons in 4 weeks.

The reader: a technical product/engineering leader who uses Claude Code daily, knows what an LLM and a prompt are, has heard "agents" and "multi-agent" talked about a lot, and wants a real mental model plus hands-on reps.

## The running use case: Kestrel

Kestrel is a FICTIONAL open-source Python image-processing library. The course's project: port Kestrel to TypeScript.

- The **real** (story) Kestrel has ~240 modules. That's the 100-agent problem in Week 4 and the capstone.
- The **starter repo** in `kestrel-starter/` is a 24-module slice of it, so every lab runs for real at small cost. Week 4 labs run 10–20 agents on cheap worker models against the 24 modules and then reason about what changes at 100 / 240.

### Starter repo layout (exact; labs must reference these paths)

```
kestrel-starter/
  README.md            how to set up and run tests
  CLAUDE.md            short repo guide for Claude Code (points to MIGRATION.md)
  MIGRATION.md         the porting rules (naming, types, test porting, known traps section left EMPTY for the reader to fill)
  pyproject.toml
  kestrel/
    core/   errors.py mathutil.py color.py geometry.py image.py
    ops/    crop.py flip.py rotate.py resize.py grayscale.py threshold.py invert.py
            brightness.py contrast.py blur.py histogram.py pad.py
    io/     ppm.py pgm.py
    analysis/ stats.py edges.py
    pipeline/ steps.py runner.py
    cli.py
  tests/    mirrors kestrel/: tests/core/test_color.py, tests/ops/test_blur.py, ... tests/test_cli.py
  ts/
    package.json       (typescript + vitest; `npm test`, `npx vitest run <file>`)
    tsconfig.json
    src/index.ts       barrel file: every ported module adds one `export * from "./<path>"` line (a deliberate merge-conflict hotspot used in Lesson 14)
    src/               ported modules go here, same layout: ts/src/core/color.ts, ts/src/ops/blur.ts
    test/              ported tests go here: ts/test/core/color.test.ts
  samples/             tiny .ppm / .pgm images (e.g. samples/tiny.ppm, samples/gradient.ppm)
  scripts/
    deps.py            prints the module dependency graph from imports. `python scripts/deps.py` (adjacency), `--layers` (topological waves), `--critical` (critical path), `--dot` (Graphviz)
    status.py          table of every module: ported? TS test present? TS test passing?  `--json` for machine output, `--next` lists modules whose deps are all ported (ready to work)
    verify.sh          `scripts/verify.sh kestrel/core/color.py` → runs the Python tests AND the TS tests for that module; exit 0 only if both pass. THIS is the loop exit condition used throughout the course.
    difftest.py        differential end-to-end test: runs a pipeline spec on every sample with Python and with the TS port, compares output bytes (`python scripts/difftest.py "gray|threshold:128"`). Needs pipeline/runner + cli + io ported.
  .claude/
    settings.json      allows Bash(python -m pytest*), Bash(npx vitest*), Bash(scripts/*), Bash(python scripts/*) so labs don't drown in permission prompts
    agents/            empty (.gitkeep) — the reader writes subagents here in Lesson 8
    workflows/         empty (.gitkeep) — the reader saves workflows here in Week 4
```

### Dependency graph (true in the repo)
- `errors`, `mathutil`: no deps
- `color` → mathutil; `geometry` → mathutil, errors
- `image` → color, geometry, errors
- every `ops/*` → image (some also color, mathutil, geometry, errors)
- `io/ppm`, `io/pgm` → image, errors
- `analysis/stats` → ops/histogram; `analysis/edges` → ops/grayscale, mathutil
- `pipeline/steps` → all ops; `pipeline/runner` → steps, errors
- `cli` → runner, io/ppm, io/pgm
- Layers (waves): L0 errors, mathutil · L1 color, geometry · L2 image · L3 the 12 ops + io/ppm + io/pgm · L4 stats, edges, steps · L5 runner · L6 cli. 7 waves; the widest wave (L3) has 14 modules. Critical path: mathutil → color → image → (any op) → steps → runner → cli (7 modules long).

### Built-in traps (the tests catch them; a naive port fails)
- **T1 rounding:** Python `round()` is banker's rounding (`round(2.5) == 2`), JS `Math.round(2.5) === 3`. Used in `color.to_gray` and `ops/blur`. `mathutil.round_half_even` exists in Python.
- **T2 floor division:** Python `//` floors toward −∞ (`-7 // 2 == -4`); JS `Math.trunc(-7/2) === -3`. Used in `mathutil.floor_div` → `geometry`, `resize`, `rotate`.
- **T3 modulo:** Python `-1 % 5 == 4`; JS `-1 % 5 === -1`. Used in `ops/pad` wrap mode.
- **T4 sorting:** JS `[10, 9, 100].sort()` sorts as strings → `[10, 100, 9]`. Bites `analysis/stats.median`.
- **T5 parsing:** PPM headers can contain `#` comments and arbitrary whitespace; `io/ppm` handles both.
`MIGRATION.md` has an empty "Known traps" section. The course has the reader's agents discover traps and append them (Lessons 3–4, 12).

## Verified Claude Code facts (Oct 2026) — use ONLY these for product specifics

If you need a product detail not listed here, describe it generally rather than inventing a flag, field, or number. Docs base: https://code.claude.com/docs/en/

**Models.** Main model: `--model`, `/model`, or `"model"` in settings.json. Aliases: `opus` (Opus 5.5), `sonnet` (Sonnet 5.5), `haiku` (Haiku 5.5), `fable` (Fable 5.1), `opusplan` (Opus while planning, Sonnet while executing), `inherit` (in agent frontmatter: use the main model). Default worker model: env var `CLAUDE_CODE_SUBAGENT_MODEL` (e.g. `haiku`). `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` forces it on all subagents. Precedence for a subagent's model, highest first: (1) the `model` parameter on that specific Agent tool call, (2) the subagent's frontmatter `model`, (3) `CLAUDE_CODE_SUBAGENT_MODEL`, (4) the main conversation's model. Effort levels: low, medium, high, xhigh, max (`/effort`, `--effort`, `effort` frontmatter).

**Subagents.** Files: `.claude/agents/*.md` (project) or `~/.claude/agents/*.md` (user); also `--agents '<json>'` for one session. Frontmatter: `name`, `description` (both required); optional `tools` (allowlist), `disallowedTools`, `model`, `effort`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation: worktree`, `color`, `initialPrompt`. Body = the subagent's system prompt. Claude decides to delegate from `description`; "use proactively" in a description encourages it. Explicit: `@agent-<name>` or "use the porter agent to…". `claude --agent <name>` runs a whole session as that agent. Each subagent gets a fresh context (its system prompt + the delegation message; CLAUDE.md loaded; NOT the parent's history); only its final report returns to the parent. Subagents can spawn subagents, up to 3 layers deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); up to 20 run concurrently by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`). Subagents can run in the background; Ctrl+B backgrounds a running task.

**Agent teams (experimental, off by default).** Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (env or settings.json `env`). The main session is the team lead; teammates are separate Claude Code instances with their own context, message each other by name (SendMessage), and share a task list with statuses and dependencies. One team per session, no nested teams, not available in `-p`/SDK mode. Docs suggest starting with 3–5 teammates. Hooks: `TeammateIdle`, `TaskCreated`, `TaskCompleted`. Costs page notes teams use roughly 7x the tokens of a single session when teammates run in plan mode.

**Workflows.** A JavaScript script that orchestrates many subagents deterministically. You ask for one in plain words ("use a workflow to…") or include the keyword `ultracode` in a prompt; `/effort ultracode` makes Claude plan workflows for every substantive task. Saved workflows live in `.claude/workflows/` (project) or `~/.claude/workflows/` and run as `/<name>`. `/workflows` shows live progress (p pause, x stop, s save). Limits: up to 16 agents run concurrently (`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, 1–256; a 4-CPU machine ran 2 at once until it was set, so Week 4 launch commands set it to 16), 1,000 agents per run, 4,096 items per parallel/pipeline call. A "Large workflow" warning appears above 25 agents (50 with `workflowSizeGuideline: "large"`) or ~1.5M projected tokens. Workflow agents have no Agent tool, so a workflow agent cannot start subagents; nest `workflow()` instead. Size guideline setting `workflowSizeGuideline`: small (<5), medium (<10, default), large (<50), unrestricted. Available on paid plans and the API; on Pro, enable "Dynamic workflows" in `/config`. Script API (plain JavaScript, not TypeScript):
```js
export const meta = { name: 'port-wave', description: 'Port one dependency wave', phases: [{title:'Port'},{title:'Verify'}] }  // pure literal
// agent(prompt, {label, phase, schema, model, effort, isolation:'worktree', agentType}) -> Promise<text | object (with schema) | null>
// parallel([() => agent(...), ...])  -> barrier, waits for all, failed items become null
// pipeline(items, stage1, stage2, ...) -> each item flows through stages independently, no barrier
// phase(title), log(message), args (input), budget.total / budget.remaining()
// workflow(nameOrRef, args) -> run another workflow as a sub-step (one level of nesting)
// No Date.now(), Math.random(), filesystem or shell in the script itself — agents do the work.
```

**Worktrees.** `claude --worktree <name>` (or `-w`) creates `.claude/worktrees/<name>/` on branch `worktree-<name>`. Subagent frontmatter `isolation: worktree` (or workflow `agent(..., {isolation:'worktree'})`) gives each agent its own temporary worktree, removed if it made no changes. `.worktreeinclude` copies git-ignored files (e.g. `node_modules`) in. Symlinks are not copied, so `node_modules/.bin` is missing until `npm rebuild` runs.

**Headless.** `claude -p "<prompt>"`; `--output-format text|json|stream-json` (json includes `total_cost_usd`, `num_turns`, and `structured_output` when `--json-schema '<schema>'` is given); `--max-turns N`; `--max-budget-usd X` (client-side estimate, can overshoot by one step); `--allowedTools "Read,Edit,Bash(scripts/*)"`; `--permission-mode acceptEdits`; `--model`; `--agents`; `--bare` (skips CLAUDE.md, hooks, plugins, MCP, subagent discovery). Running many in parallel from bash is plain shell (`&`, `xargs -P`), not a built-in feature; say so.

**Loops & hooks.** `/loop 5m <prompt>` repeats on an interval; `/loop <prompt>` self-paces. **Stop hook**: a command in settings.json `hooks.Stop` that runs when Claude tries to finish; exiting with code 2 (stderr = reason) or printing `{"decision":"block","reason":"..."}` sends Claude back to work. Hook commands run in Claude's current directory; use `$CLAUDE_PROJECT_DIR` for project paths. Input JSON includes `stop_hook_active` (true if already continuing because of a stop hook — check it to avoid infinite loops). Claude Code caps consecutive stop-hook continuations at 8 (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`), resetting when Claude calls a tool. `SubagentStop` works the same for subagents (input includes `agent_type`). `/usage` (alias `/cost`) shows session cost.

Stop hook example (settings.json, valid shape):
```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/scripts/stop_gate.py\"" } ] }
    ]
  }
}
```
(`scripts/stop_gate.py` is something the reader writes in Lesson 4: read JSON from stdin, if `stop_hook_active` is true exit 0; otherwise run `scripts/status.py --json`, and if any module that has a TS file fails its tests, print the failures to stderr and exit 2.)

**Agent SDK.** Python `claude-agent-sdk` (`from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition`), TypeScript `@anthropic-ai/claude-agent-sdk`. `AgentDefinition(description=..., prompt=..., tools=[...], model="sonnet")`; options `agents={...}`, `allowed_tools=[..., "Agent"]`, `max_turns`, `max_budget_usd`, `model`, `hooks`, `permission_mode`, `cwd`. Mention as the "same ideas in code" path; labs use the CLI.

**Anthropic's published guidance.**
- "Building effective agents" (https://www.anthropic.com/engineering/building-effective-agents): workflow patterns prompt chaining, routing, parallelization (sectioning & voting), orchestrator-workers, evaluator-optimizer; agents = LLMs using tools in a loop; start with the simplest thing that works.
- "How we built our multi-agent research system" (https://www.anthropic.com/engineering/multi-agent-research-system): a lead agent with parallel subagents outperformed a single agent by 90.2% on their internal research eval; agents use ~4x the tokens of chat and multi-agent systems ~15x; token usage alone explained ~80% of performance variance on their browsing eval; parallelism cut research time up to 90%; multi-agent fits poorly when agents need shared context or have many dependencies, which includes most coding tasks. USE THIS LAST POINT: it is exactly why a migration needs a dependency graph, contracts, and isolation before it can be parallelized.

## Concepts the course must teach (vocabulary)

- **Agent = model + tools + loop.** The loop: gather context → act → check → repeat until a stop condition.
- **Loop engineering:** designing the stop conditions (success check, max turns, budget, no-progress detection), what happens each iteration, where verification sits, and loops *between* agents (implement → review → fix; evaluator-optimizer), and loops at scale (retry, idempotency, circuit breakers, loop-until-dry).
- **Graph engineering:** picking and wiring the shape of the work. Nodes = agents or steps; edges = handoffs. Shapes: **chain** (sequential pipeline), **diamond** (fan-out → fan-in: one splitter, N parallel workers, one merger), **double diamond** (diverge → converge → diverge → converge: explore several approaches, converge on one plan, fan out to build, converge to integrate/verify; borrowed from the design-thinking Double Diamond: discover/define, develop/deliver), **tree / hierarchy** (orchestrators of orchestrators), **DAG** (dependency graph, waves, critical path), **cycle** (a loop edge back: review → fix). Also communication topology: hub-and-spoke, hierarchy, mesh, blackboard.
- When to use which: double diamond when the *approach* is uncertain (explore before committing) AND the execution is parallelizable; single diamond when the approach is known and the work splits cleanly; chain when each step needs the previous step's output; cycle when quality needs iteration against a checkable bar; tree when one coordinator can't hold N reports (span of control ~5–10).
- Amdahl-style limit: speedup is bounded by the critical path (7 waves) and by coordination/merge cost, so more agents eventually make it slower and pricier.

## Writing style

- Plain, direct English. Short sentences. Explain every term the first time. A knowledgeable person talking.
- Avoid: em-dash asides (use them rarely, at most one or two per lesson), "not X, but Y" framing, colon-then-reveal, scare quotes, "worth noting", "honest caveat", "journey", "delve", emoji.
- Concrete over abstract: every idea lands on Kestrel with real file names, real numbers.
- Each lesson ~12–18 min of reading + lab. Roughly 1,400–2,200 words of prose plus components.
- Never claim a number or flag not in the facts above. Toy numbers you invent for illustration must be labelled as illustrative.
- Use `<code>` for file names, flags, commands.

## Lesson HTML contract

Each lesson is ONE file `lessons/lesson-NN.html` containing exactly one `<section>`. No `<style>`, no `<script>`, no HTML comments containing `--` sequences. Valid, closed HTML; double-quoted attributes. Escape `<`, `>`, `&` inside code as `&lt;` `&gt;` `&amp;`.

```html
<section class="lesson" id="lesson-07" data-week="2" data-title="Orchestrator and worker models" data-minutes="15">
  <div class="lesson__eyebrow">
    <span class="chip">Lesson 07</span>
    <span class="meta">Week 2 · Small teams</span>
    <span class="meta">~15 min</span>
    <span class="scale" data-scale="3-5">3–5 agents</span>
  </div>
  <h1>Orchestrator and worker models</h1>
  <p class="lesson__deck">One or two sentences that set up the lesson.</p>
  <hr class="rule-sep">
  <h2><span class="h2num">Part one</span>Heading</h2>
  <p>…</p>
  … parts, components …
  <div class="lab wide" …>…</div>
  <div class="c-takeaway"><div class="label">Key takeaway</div><p>One or two sentences.</p></div>
  <div class="teaser"><b>Next</b>Lesson 08 · Title. One sentence.</div>
</section>
```
`data-scale` values: `1`, `3-5`, `10-25`, `100`. Week names: Week 1 · One agent, Week 2 · Small teams, Week 3 · Systems, Week 4 · Scale. For lesson 20 the teaser says the course is complete and points to the Reference appendix.

Direct children of the section sit in a 68ch reading column. Add class `wide` to break out wider (exercises, tables, code, diagrams, labs).

### Components (use the exact markup; the page's JS wires them by `data-component`)

Every lesson must contain: at least one `predict`, at least one `mcq`, at least one graph figure OR stepper, one `lab`, the takeaway and teaser. Use `verdict`, `code`, `stepper` where they help. Lessons 6 and 19 also include the `scale-sim`.

**1. Predict-then-reveal**
```html
<div class="ex wide c-predict" data-component="predict">
  <div class="ex__head"><span class="dot"></span><span class="label">Predict first</span></div>
  <div class="ex__body">
    <p>Question for the reader to answer in their head.</p>
    <div class="btn-row"><button class="btn" data-reveal aria-expanded="false">Reveal</button></div>
    <div class="c-reveal" data-reveal-panel><div class="c-reveal__inner"><div class="c-reveal__card">
      <div class="label">The answer</div>
      <p>…</p>
    </div></div></div>
  </div>
</div>
```

**2. Multiple choice** (every option gets its own feedback; exactly one `data-correct="true"`)
```html
<div class="ex wide c-mcq" data-component="mcq">
  <div class="ex__head"><span class="dot"></span><span class="label">Check yourself</span></div>
  <div class="ex__body">
    <p>Question</p>
    <ul class="c-mcq__opts">
      <li><button class="opt" data-fb="a" data-correct="false"><span class="k">A</span><span class="t">Option text</span><span class="mk" aria-hidden="true"></span></button></li>
      … b, c, d …
    </ul>
    <div class="c-mcq__fb">
      <div class="fb is-shown" data-fb="idle" data-verdict="idle"><div class="vd">Pick one</div><p>Every option has a reason attached.</p></div>
      <div class="fb" data-fb="a" data-verdict="wrong"><div class="vd">Not this one</div><p>Why.</p></div>
      <div class="fb" data-fb="c" data-verdict="right"><div class="vd">Yes</div><p>Why.</p></div>
      …
    </div>
  </div>
</div>
```

**3. Verdict** (make-the-call on a scenario; two or three buttons; one right answer named in `data-answer`)
```html
<div class="ex wide c-verdict" data-component="verdict" data-answer="team">
  <div class="ex__head"><span class="dot"></span><span class="label">Make the call</span></div>
  <div class="ex__body">
    <p>Scenario intro.</p>
    <div class="spec-card"><div class="label">The situation</div><ol><li>fact</li><li>fact</li></ol></div>
    <div class="verdict-row">
      <button class="vbtn" data-pick="one">One agent</button>
      <button class="vbtn" data-pick="team">A team</button>
    </div>
    <div class="stack">
      <div class="vfb is-shown" data-for="idle"><p>Decide, then see the reasoning.</p></div>
      <div class="vfb" data-for="one"><span class="verdict-tag" data-v="fail">Not quite</span><p>Why.</p></div>
      <div class="vfb" data-for="team"><span class="verdict-tag" data-v="pass">Right call</span><p>Why.</p></div>
    </div>
  </div>
</div>
```

**4. Annotated code** (click a marked line → note). Lines that are not clickable use `<div class="cl">`. Token classes: `tk-kw` keyword, `tk-str` string, `tk-com` comment, `tk-num` number, `tk-key` JSON/YAML key.
```html
<div class="c-code wide" data-component="code">
  <div class="c-code__head"><span>.claude/agents/porter.md</span><span class="tag">Click a marked line</span></div>
  <div class="c-code__grid">
    <ol class="c-code__lines">
      <li><button class="cl" data-note="n1"><span class="ln">1</span><pre>---</pre></button></li>
      <li><div class="cl"><span class="ln">2</span><pre><span class="tk-key">name</span>: porter</pre></div></li>
    </ol>
    <div class="c-code__notes">
      <div class="cnote cnote--idle is-shown" data-note="idle"><div class="label">Annotations</div><p>Click a marked line.</p></div>
      <div class="cnote" data-note="n1"><div class="label">Line 1 · frontmatter</div><p>…</p></div>
    </div>
  </div>
</div>
```

**5. Graph figure** (static diagram; inline SVG). Use the shared classes; the page provides arrow markers `url(#arr)` and `url(#arr-accent)`. Keep text ≥ 12px in viewBox units at ~720 wide. Every shape has an explicit class; do not set fill/stroke colors inline.
```html
<figure class="graph wide">
  <svg viewBox="0 0 720 260" role="img" aria-label="Diamond: one planner fans out to three porters, then a merger">
    <g class="g-node g-node--orch" data-node="plan"><rect x="20" y="105" width="120" height="50" rx="8"/><text x="80" y="135">Planner</text></g>
    <g class="g-node g-node--worker" data-node="p1"><rect x="300" y="20" width="120" height="50" rx="8"/><text x="360" y="50">Porter A</text></g>
    <path class="g-edge" data-edge="e1" d="M140 130 C 220 130, 220 45, 300 45"/>
    <path class="g-edge g-edge--loop" d="…"/>   (loop/feedback edge: dashed accent)
    <text class="g-cap" x="…" y="…">small annotation</text>
  </svg>
  <figcaption>Caption sentence.</figcaption>
</figure>
```
Node kinds: `g-node--orch` (orchestrator/lead), `g-node--worker`, `g-node--check` (verifier/reviewer/test), `g-node--data` (file, shared state, status board), `g-node--human`. Text inside nodes is auto-centered (text-anchor middle) by CSS; give x at the rect center and y at center + 5. Edges: `g-edge` (solid, arrow), `g-edge g-edge--loop` (dashed accent, arrow), `g-edge g-edge--faint`.

**6. Stepper** (animated walk through a graph or loop; frame i lights the listed nodes and edges and shows its caption)
```html
<div class="ex wide c-stepper" data-component="stepper">
  <div class="ex__head"><span class="dot"></span><span class="label">Step through it</span></div>
  <div class="ex__body">
    <div class="stepper__view">
      <svg viewBox="0 0 720 240" role="img" aria-label="…"> … nodes with data-node, edges with data-edge … </svg>
    </div>
    <ol class="stepper__frames">
      <li data-on="plan" data-edges="">The planner reads <code>scripts/deps.py --layers</code>…</li>
      <li data-on="plan,p1,p2,p3" data-edges="e1,e2,e3">It fans out…</li>
    </ol>
  </div>
</div>
```
(The JS adds Prev/Next controls and a counter. Use 4–8 frames.)

**7. Lab** (hands-on in Claude Code; every lesson has exactly one)
```html
<div class="lab wide" data-component="lab" data-lab-id="lab-07">
  <div class="lab__head">
    <span class="label">Lab 07 · In Claude Code</span>
    <span class="lab__meta">~15 min · est. $0.30–$1.00</span>
  </div>
  <div class="lab__body">
    <p class="lab__goal"><b>Goal.</b> One sentence.</p>
    <ol class="lab__steps">
      <li><p>Instruction.</p>
        <div class="cmd"><pre><code>cd kestrel-starter
claude --model opus</code></pre></div>
      </li>
      <li><p>Create this file.</p>
        <div class="cmd" data-file=".claude/agents/porter.md"><pre><code>---
name: porter
…</code></pre></div>
      </li>
      <li><p>Type this prompt into Claude Code.</p>
        <div class="cmd" data-kind="prompt"><pre><code>Port kestrel/core/color.py …</code></pre></div>
      </li>
    </ol>
    <div class="lab__expect"><div class="label">What you should see</div><p>…</p></div>
    <div class="lab__stretch"><div class="label">Stretch</div><p>Optional harder variation.</p></div>
  </div>
</div>
```
`data-kind="prompt"` marks a block that is a prompt typed into Claude Code (vs a shell command). Copy buttons and the "I ran this" checkbox are added by JS. Costs are rough estimates, labelled "est.". Always use bounded runs: `--max-budget-usd` and/or `--max-turns` in headless runs; cheap worker models (`haiku`/`sonnet`) for multi-agent labs.

**8. Scale simulator** (lessons 6 and 19 only; self-contained, just drop it in)
```html
<div class="ex wide c-sim" data-component="scale-sim" data-modules="240" data-waves="7" data-start="5"></div>
```

**Static pieces**
- `<div class="c-note"><p><b>Lead-in.</b> aside text</p></div>`
- `<div class="quote"><div class="quote__from">Agent report</div><p>…</p></div>` (add class `quote--agent` for an agent's words)
- Tables: `<div class="c-table-wrap wide"><table class="c-table"><thead>…</thead><tbody>…</tbody></table></div>` then optional `<p class="tbl-cap wide">caption</p>`.
- Transcript of an agent loop: `<div class="trace wide"><div class="trace__row" data-kind="think|tool|result|stop"><span class="trace__k">tool</span><span class="trace__v">Bash: scripts/verify.sh kestrel/core/color.py</span></div>…</div>`

## Syllabus (each writer owns one week; follow these outlines, you may improve within them)

### Week 1 · One agent (scale 1)
**L01 What an agent actually is** (~14 min). Agent = model + tools + loop. Contrast: chat (one answer) vs workflow (code decides the steps) vs agent (model decides the next step). Anatomy of one turn on Kestrel. Trace component showing a real-looking loop (Read → Bash pytest → Edit → Bash). Graph: the loop as a cycle. Lab 01: download/unzip starter, `python -m pytest`, `cd ts && npm install`, open `claude`, ask it to explain the repo and run `python scripts/deps.py --layers`; observe each tool call = one loop iteration; `/usage` at the end.
**L02 Designing the loop** (~15 min). Loop engineering intro. Four stop conditions: success check, turn cap, budget cap, no-progress. What runs each iteration. Failure modes: stopping early ("looks done"), never stopping, thrashing. Stepper through iterations. Lab 02: headless bounded run: `claude -p "Port kestrel/core/mathutil.py and its tests to ts/… Run scripts/verify.sh kestrel/core/mathutil.py until it passes." --max-turns 20 --max-budget-usd 1 --output-format json --permission-mode acceptEdits` then read `num_turns`, `total_cost_usd`, `is_error`/subtype. Mention the T2 floor-division trap likely appears.
**L03 Context is the bottleneck** (~14 min). What the agent sees: system prompt, CLAUDE.md, the files it reads, tool output. Context window as working memory; why "read everything" hurts; MIGRATION.md as a contract; context rot over long sessions; compaction. Lab 03: same port of `color.py` twice — once with `--bare` (no CLAUDE.md) and once normal — compare whether it follows MIGRATION.md naming and finds T1; then have it append the trap to MIGRATION.md "Known traps".
**L04 Verification is the exit condition** (~16 min). "Done" must be checkable. Tests as oracle; scripts/verify.sh; the T1 banker's rounding trap as the story (agent says done, test fails). Stop hook to make "done" mechanical: settings.json `hooks.Stop`, `stop_hook_active`, the 8-continuation cap, exit code 2. Annotated code of `scripts/stop_gate.py` (~25 lines Python) and the settings.json. Lab 04: write stop_gate.py + hook in `.claude/settings.local.json`, port `ops/blur.py`, watch the hook send it back.
**L05 One module end to end, and when one agent is enough** (~15 min). The complete single-agent recipe (context file, bounded loop, verification gate, cost cap). Port geometry + image. Record baseline: turns, cost, wall-clock per module (table template). When to graduate to a team: context overflow, independent parallel work, need for independent judgement, wall-clock pressure. When NOT to: tightly coupled work (cite the Anthropic research post point about coding). Verdict exercises. Lab 05: port geometry + image in one session with the stop hook; fill the baseline table.

### Week 2 · Small teams (scale 3–5)
**L06 Why split, and what it costs** (~15 min). Four reasons to split: context isolation, parallelism, specialization, independent judgement. Costs: tokens (~4x agent vs chat, ~15x multi-agent per Anthropic), coordination overhead, lossy handoffs (only the final report returns). scale-sim component. Lab 06: in one session ask Claude to use 3 subagents in parallel to port `ops/invert.py`, `ops/flip.py`, `ops/crop.py`; compare wall-clock and `/usage` with the L05 baseline.
**L07 Orchestrator and worker models** (~15 min). The orchestrator plans, routes, judges; workers execute narrow tasks. Model selection: main `--model opus`, `CLAUDE_CODE_SUBAGENT_MODEL=haiku|sonnet`, frontmatter `model`, per-call model, precedence list, `opusplan`, effort. Where to spend the expensive model: orchestrator and reviewer, rarely bulk workers. Table of role → model → why. Lab 07: `CLAUDE_CODE_SUBAGENT_MODEL=haiku claude --model opus`, port 3 ops with subagents, then repeat with `sonnet` workers; compare pass rate on first try and cost.
**L08 Defining subagent roles** (~16 min). `.claude/agents/` files: planner (read-only tools, produces plan), porter (Read, Edit, Write, Bash), reviewer (read-only + Bash for tests, never edits). Frontmatter fields that matter: description (drives delegation), tools allowlist, model, effort, maxTurns. Annotated code of porter.md. Least privilege. Lab 08: write the three agent files, then `Use the planner agent to plan io/, then the porter agent for each module, then the reviewer agent`.
**L09 Graph shapes: chain, diamond, double diamond** (~17 min). THE graph-engineering lesson. Chain, diamond, double diamond (diverge-converge twice; origins in the design-thinking Double Diamond), tree, cycle. Decision guide table: shape → use when → Kestrel example → risk. Steppers for diamond and double diamond. Verdict exercises choosing a shape. Lab 09: run a double diamond by prompt: 3 subagents each propose a strategy for porting `ops/` (e.g. by-file, by-trap, test-first), orchestrator picks/merges into a plan (converge), 3 porters execute in parallel (diverge), reviewer integrates and runs verify (converge).
**L10 Loops between agents** (~16 min). Evaluator-optimizer: porter ↔ reviewer cycle. Convergence: a checkable rubric, max rounds (e.g. 3), progress detection (same failure twice = stop and escalate), reviewer independence (fresh context, different model). Ping-pong failure. SubagentStop hook. Stepper of a 3-round loop on `ops/pad.py` (T3 modulo). Lab 10: porter/reviewer loop with max 3 rounds on `ops/pad.py` and `analysis/stats.py` (T4).

### Week 3 · Systems (scale 10–25)
**L11 Work as a dependency graph** (~16 min). DAG, topological order, waves, width (max useful parallelism = 14 at wave L3), critical path (7). Why "most coding tasks" fit multi-agent poorly until you find the graph. Graph figure of Kestrel's 7 waves. Lab 11: `python scripts/deps.py --layers` and `--critical`; ask the orchestrator to write `PLAN.md` with waves and agent assignments; port wave L0–L2 sequentially, then L3 with parallel subagents.
**L12 Handoffs, contracts and shared state** (~15 min). Lossy handoffs; contract = structured output (`--json-schema` with fields module, status, tests_passed, traps_found, notes); single source of truth = `scripts/status.py` (derived from the repo, not from agent claims); blackboard pattern; single-writer rule for shared files (MIGRATION.md traps). Annotated code of a JSON schema. Lab 12: run 4 headless ports in parallel from bash with `--json-schema`, `&` and `wait`, collect results into `results/*.json`, reconcile against `scripts/status.py --json`.
**L13 Who talks to whom** (~15 min). Topologies: hub-and-spoke (subagents → parent only), hierarchy (nested subagents, depth 3), mesh (agent teams: SendMessage + shared task list), blackboard (shared files). Channel count n(n−1)/2 for mesh. Failure modes per topology. Agent teams experimental: enable, lead, teammates, task list, 3–5 to start, ~7x tokens note. Lab 13: enable agent teams, lead + 3 teammates (io, analysis, pipeline/steps) sharing a task list with dependencies; compare with hub-and-spoke from L11.
**L14 Keeping agents out of each other's way** (~16 min). Parallel writers collide: shared files (`ts/src/index.ts` barrel), lockfiles, generated files. Isolation with worktrees (`isolation: worktree`, `claude -w`, `.worktreeinclude` for node_modules). Ownership rules (each agent owns its module's files; barrel edits deferred to an integrator). Merge strategies: integrator agent, append-only files, regenerate barrel from status. Lab 14: add `isolation: worktree` to porter, port 4 ops in parallel, watch the barrel conflict, then fix the design by having porters not touch the barrel and an integrator regenerate it.
**L15 Testing a team** (~15 min). Per-node checks (module tests) vs end-to-end (difftest.py comparing Python vs TS output bytes). Why a team can pass every unit and still fail end to end (contract drift between modules). Attribution: which node broke it; trace reading. Lab 15: after porting pipeline/runner + cli + io, run `python scripts/difftest.py "gray|threshold:128"` and a couple more specs; have a debugging subagent bisect a failing spec to a module.

### Week 4 · Scale (scale 100)
**L16 Workflows: orchestration as code** (~17 min). Model-driven orchestration (Claude decides who to spawn) vs scripted (a workflow script decides; deterministic loops, fan-out, conditionals). The script API. Annotated code of a full `port-wave` workflow using pipeline(modules, port, verify) with schema. Saving to `.claude/workflows/`, running `/port-wave`, `/workflows` view. Limits (16 concurrent, 1,000/run, size guideline, Large workflow warning). Lab 16: "use a workflow to port every module in the next ready wave (`python scripts/status.py --next`), one agent per module, each verifies with scripts/verify.sh" with `CLAUDE_CODE_SUBAGENT_MODEL=haiku`; watch `/workflows`; save it.
**L17 Orchestrators of orchestrators** (~16 min). Span of control: a coordinator reading 100 reports drowns; trees: 1 lead → 5–10 sub-leads → 10 workers each. Summaries compress upward. Depth limits (subagents 3 layers; `workflow()` nests one level). Kestrel-240 tree: per-package sub-leads. Graph figure of the tree. Lab 17: workflow with one sub-lead stage per package (core, ops, io, analysis, pipeline) that returns a 5-line summary; the top lead only reads summaries.
**L18 Loops at scale** (~17 min). At 100 agents, something is always failing. Retries with a cap; idempotency (check `status.py` before porting, safe to rerun); circuit breaker (stop the wave if >30% fail — illustrative threshold); loop-until-dry for discovery (find traps until two rounds find nothing new); budgets (`--max-budget-usd`, workflow `budget`); killing a runaway (`/workflows` x, Esc). Annotated code of the retry+breaker loop. Lab 18: deliberately break `kestrel/core/mathutil.py`'s TS port (or a dependency) and watch the breaker stop the wave instead of burning 14 agents.
**L19 Tracing, cost, and when 100 is worse than 10** (~16 min). Cost model: tokens ≈ cost; per-module cost × modules + coordination. Amdahl: 240 modules, 7 waves, widest wave ~ (story) 140 modules → speedup ceiling. Merge/coordination tax rises with N. scale-sim component. 16-concurrency default and why. Lab 19: port all remaining starter modules with 10–20 haiku workers via a workflow, record cost per module and wall-clock, then extrapolate in a table to 240 modules at 10, 25, 100 agents (mark extrapolation as estimate).
**L20 Capstone: design the 100-agent migration** (~20 min). Put it together for Kestrel-240: double diamond at the top (explore 3 strategies → choose), DAG waves, hierarchical leads, worktrees, verify loops, differential e2e, budgets and breakers, human checkpoints. Full graph figure. A decision guide: 1 vs 3–5 vs 10–25 vs 100 agents. MCQs reviewing design choices. Lab 20: write `.claude/workflows/migrate.js` that implements the full design against the 24-module starter (dry run with a `--small` arg limiting to one wave first), run it, then write a one-page retrospective.
