## What changed

## How it was checked

- [ ] `python3 course/build.py && python3 course/tests/check_course.py` (course changes)
- [ ] `node course/tests/smoke.mjs` (course changes)
- [ ] `cd kestrel-starter && python -m pytest -q` (starter changes)
- [ ] `ci/check_traps.sh` (starter or trap fixture changes)
