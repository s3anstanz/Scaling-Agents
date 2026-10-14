# scaling-agents

The source for the course "Scaling Agents: From One to One Hundred" and its practice codebase.

- `kestrel-starter/` is what learners copy out and port. Its Python code and tests are the specification; keep its scripts' output matching what lessons quote (CI checks the waves, critical path and status lines).
- `course/lessons/lesson-NN.html` are lesson fragments. Follow `course/AUTHORING.md`. Never add `<script>`, `<style>` or HTML comments to a lesson.
- `ci/trap-fixtures/` holds a naive and a correct port of `core/mathutil`. If you change that module or its tests, update the fixtures.
- Before opening a PR run: `ruff check .`, `python3 course/build.py`, `python3 course/tests/check_course.py`, `node course/tests/smoke.mjs`, `(cd kestrel-starter && python -m pytest -q)` and `ci/check_traps.sh`.
- `main` is protected: work on a branch and open a PR.
