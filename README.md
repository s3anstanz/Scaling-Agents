# Scaling Agents: From One to One Hundred

A hands-on course in Claude Code. You start with one agent working in a loop and finish by designing a hundred agents that port a whole codebase together. Two skills run through all twenty lessons: **loop engineering** (when an agent stops, what it may spend, how "done" is checked) and **graph engineering** (the shape of a team: chain, diamond, double diamond, tree, dependency graph, cycle).

- **Course:** [open it in Claude](https://claude.ai/artifact/MEMDxrrDeJUpgEHdfCJDf5) (private to the owner until shared)
- **Project:** port Kestrel, a fictional Python image-processing library, to TypeScript

| Week | Scale | Lessons |
|---|---|---|
| 1 · One agent | 1 | What an agent is · Designing the loop · Context · Verification as the exit condition · One module end to end |
| 2 · Small teams | 3–5 | Why split · Orchestrator and worker models · Subagent roles · Graph shapes · Loops between agents |
| 3 · Systems | 10–25 | Dependency graphs · Handoffs and contracts · Topology · Isolation with worktrees · Testing a team |
| 4 · Scale | 100 | Workflows · Orchestrators of orchestrators · Loops at scale · Cost and when 100 is worse than 10 · Capstone |

## Taking the course

You need Claude Code, Python 3.11+, Node.js 22.12+ and git. Lab 01 walks through this:

```bash
git clone https://github.com/s3anstanz/scaling-agents.git
cp -R scaling-agents/kestrel-starter ./kestrel-starter
cd kestrel-starter
git init && git add -A && git commit -m "Kestrel starter"
```

Every lab runs in that copy, never in this repo. The copy is your own git repo; push it wherever you like. Week 4 makes a second copy (`kestrel-scale/`) the same way.

## What's in this repo

```
kestrel-starter/   the practice codebase: 24 Python modules, 142 tests, an empty TypeScript project, lab scripts
course/            the course source: 20 lessons, page shell, build script and tests
ci/                the trap guard: proves a naive port fails and a correct one passes
.github/           CI and security workflows, Dependabot, the main-branch ruleset
```

## Working on the course

```bash
cd course && npm ci && npx playwright install chromium
python3 build.py                 # writes course/dist/scaling-agents.html (embeds a zip of kestrel-starter)
python3 tests/check_course.py    # lesson structure, quiz answers, stepper ids, workflow scripts parse
node tests/smoke.mjs             # every page at desktop and phone width, plus the interactive pieces

cd ../kestrel-starter && python -m pytest -q
cd ts && npm ci && cd ../.. && ci/check_traps.sh
```

Lessons follow the contract in [`course/AUTHORING.md`](course/AUTHORING.md). To update the published page, build it and republish `course/dist/scaling-agents.html` to the same artifact.
