# Scaling Agents: From One to One Hundred

Learn to build teams of AI agents in Claude Code by doing it. Across 20 short lessons you use Claude Code to port a small, made-up Python library called Kestrel to TypeScript: first with one agent, then a team of 3 to 5, then 10 to 25, and finally a design for 100.

> This repo and the course page are private. If a link below doesn't open, ask the owner to share it with you.

## Start in 4 steps

Commands are for macOS or Linux.

### 1. Check your tools

```bash
claude --version
git --version
python3 --version
node --version
```

You need Claude Code, git, Python 3.11 or newer, and Node.js 22.12 or newer. Install anything missing: [Claude Code](https://code.claude.com/docs), [Python](https://www.python.org/downloads/), [Node.js](https://nodejs.org/).

### 2. Make your own copy of the practice project

```bash
git clone https://github.com/s3anstanz/scaling-agents.git
cp -R scaling-agents/kestrel-starter ./kestrel-starter
cd kestrel-starter
git init -q && git add -A && git commit -qm "Kestrel starter"
```

You do every lab inside `kestrel-starter`. Leave the `scaling-agents` folder alone.

### 3. Install and check it works

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
(cd ts && npm ci)
python -m pytest -q
```

The last line should end with `142 passed`. Run `source .venv/bin/activate` again whenever you open a new terminal.

### 4. Start the course

[**Open the course**](https://claude.ai/artifact/MEMDxrrDeJUpgEHdfCJDf5) and start with Lesson 1.

## How the course works

- Each lesson takes about 15 minutes to read and ends with a lab you run in Claude Code. The lab tells you what to type and what you should see.
- Each lab shows an estimated cost. Type `/usage` in Claude Code to see what you've spent.
- Tick **I ran this lab** at the end of a lab to mark it done in the sidebar.

| Week | Agents | You learn |
|---|---|---|
| 1 | 1 | What an agent is, how its loop stops, and how to check its work |
| 2 | 3 to 5 | Splitting work across a small team, choosing models, and shaping the team |
| 3 | 10 to 25 | Planning around dependencies, handing work between agents, and keeping them out of each other's way |
| 4 | 100 | Scripted workflows, teams of teams, and when more agents cost more than they save |

## If something goes wrong

- **`python3 --version` or `node --version` is too old:** install a newer version from the links in step 1.
- **`npm ci` fails:** check that `node --version` shows v22.12 or newer.
- **You want a clean start:** delete both the `kestrel-starter` and `scaling-agents` folders, then repeat steps 2 and 3.

## Working on the course itself

See [CONTRIBUTING.md](CONTRIBUTING.md).
