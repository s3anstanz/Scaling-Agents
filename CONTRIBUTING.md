# Working on the course

## What's in this repo

```
kestrel-starter/   the practice project learners copy: 24 Python modules, 142 tests, an empty TypeScript project, lab scripts
course/            the course source: 20 lessons, page shell, build script and tests
ci/                the trap guard: proves a naive port fails and a correct one passes
.github/           CI and security workflows, Dependabot, the main-branch ruleset
```

## Build and test

```bash
cd course && npm ci && npx playwright install chromium
python3 build.py                 # writes course/dist/scaling-agents.html (embeds a zip of kestrel-starter)
python3 tests/check_course.py    # lesson structure, quiz answers, stepper ids, workflow scripts parse
node tests/smoke.mjs             # every page at desktop and phone width, plus the interactive pieces

cd ../kestrel-starter && python -m pytest -q
cd ts && npm ci && cd ../.. && ci/check_traps.sh
```

Lessons follow the contract in [`course/AUTHORING.md`](course/AUTHORING.md). Merging to `main` publishes the page: the Pages workflow builds `course/dist/scaling-agents.html` and serves it at https://s3anstanz.github.io/Scaling-Agents/.

`main` is protected: open a pull request from a branch. It merges once the required check, **All checks pass**, is green and every review thread is resolved.
