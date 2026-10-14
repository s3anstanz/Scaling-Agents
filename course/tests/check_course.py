"""Structural checks for every lesson, the shell script and the workflow scripts shown in lessons."""
import html
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

COURSE = Path(__file__).resolve().parent.parent
LESSONS = sorted((COURSE / "lessons").glob("lesson-*.html"))
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "rect", "circle", "line", "ellipse", "polygon", "polyline", "stop", "use"}
WORKFLOW_STUBS = (
    "const agent = async () => null, parallel = async () => [], pipeline = async () => [];\n"
    "const phase = () => {}, log = () => {}, workflow = async () => null;\n"
    "const args = {}, budget = { total: null, spent: () => 0, remaining: () => Infinity };\n"
)


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.elements = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()

    def handle_comment(self, data):
        self.errors.append("HTML comment found")


def classes(attrs):
    return set((attrs.get("class") or "").split())


def check_lesson(path: Path) -> list[str]:
    text = path.read_text()
    doc = Doc()
    doc.feed(text)
    doc.close()
    errs = list(doc.errors)
    if doc.stack:
        errs.append(f"unclosed tags: {doc.stack}")
    num = path.stem.split("-")[1]
    sections = [a for t, a in doc.elements if t == "section"]
    if len(sections) != 1:
        errs.append(f"expected 1 <section>, found {len(sections)}")
    else:
        s = sections[0]
        if s.get("id") != f"lesson-{num}":
            errs.append(f"section id {s.get('id')!r} != lesson-{num}")
        if s.get("data-week") not in {"1", "2", "3", "4"} or not s.get("data-title"):
            errs.append("section needs data-week 1..4 and data-title")
    if re.search(r"<(script|style)\b", text):
        errs.append("lessons may not contain <script> or <style>")

    comps = [a.get("data-component") for _, a in doc.elements if a.get("data-component")]
    for need in ("predict", "mcq"):
        if need not in comps:
            errs.append(f"missing a {need} component")
    if comps.count("lab") != 1:
        errs.append(f"expected exactly 1 lab, found {comps.count('lab')}")
    if not any("graph" in classes(a) for _, a in doc.elements) and "stepper" not in comps:
        errs.append("needs a graph figure or a stepper")
    for cls in ("c-takeaway", "teaser"):
        if not any(cls in classes(a) for _, a in doc.elements):
            errs.append(f"missing .{cls}")

    for block in re.findall(r'data-component="mcq".*?</ul>\s*<div class="c-mcq__fb">.*?</div>\s*</div>\s*</div>', text, re.S):
        correct = block.count('data-correct="true"')
        if correct != 1:
            errs.append(f"an mcq has {correct} correct options")
        for key in re.findall(r'class="opt" data-fb="([^"]+)"', block):
            if f'class="fb" data-fb="{key}"' not in block and f'class="fb is-shown" data-fb="{key}"' not in block:
                errs.append(f"mcq option {key!r} has no feedback panel")
    for answer, block in re.findall(r'data-component="verdict" data-answer="([^"]+)"(.*?)class="stack"', text, re.S):
        if f'data-pick="{answer}"' not in block:
            errs.append(f"verdict answer {answer!r} has no matching button")
    for block in re.findall(r'data-component="stepper"(.*?)</ol>', text, re.S):
        nodes = set(re.findall(r'data-node="([^"]+)"', block))
        edges = set(re.findall(r'data-edge="([^"]+)"', block))
        for on, ed in re.findall(r'<li data-on="([^"]*)" data-edges="([^"]*)"', block):
            missing = {n for n in on.split(",") if n.strip()} - nodes | {e for e in ed.split(",") if e.strip()} - edges
            if missing:
                errs.append(f"stepper frame references unknown ids {sorted(missing)}")
    for block in re.findall(r'data-component="code"(.*?)class="c-code__notes"(.*?)</div>\s*</div>\s*</div>', text, re.S):
        notes = set(re.findall(r'class="cnote[^"]*" data-note="([^"]+)"', block[1]))
        for ref in re.findall(r'data-note="([^"]+)"', block[0]):
            if ref not in notes:
                errs.append(f"code line points at missing note {ref!r}")
    return errs


def workflow_scripts() -> list[tuple[str, str]]:
    found = []
    for path in LESSONS:
        for code in re.findall(r"<code>(.*?)</code>", path.read_text(), re.S):
            src = html.unescape(re.sub(r"<[^>]+>", "", code))
            if "export const meta" in src and src.count("\n") >= 3:
                found.append((path.name, src))
    return found


def node_check(source: str) -> str | None:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(source)
    proc = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
    Path(f.name).unlink()
    return None if proc.returncode == 0 else proc.stderr.strip().splitlines()[-1]


def main() -> int:
    failures = 0
    if len(LESSONS) != 20:
        print(f"FAIL expected 20 lessons, found {len(LESSONS)}")
        failures += 1
    for path in LESSONS:
        errs = check_lesson(path)
        for e in errs:
            print(f"FAIL {path.name}: {e}")
        failures += len(errs)

    err = node_check((COURSE / "shell.js").read_text())
    if err:
        print(f"FAIL shell.js: {err}")
        failures += 1

    scripts = workflow_scripts()
    for name, src in scripts:
        body = src.replace("export const meta", "const meta", 1)
        err = node_check(WORKFLOW_STUBS + "async function run() {\n" + body + "\n}\nexport default run;\n")
        if err:
            print(f"FAIL {name}: workflow script does not parse: {err}")
            failures += 1
        meta = re.search(r"export const meta = \{(.*?)\n\}", src, re.S)
        phases = set(re.findall(r"title:\s*'([^']+)'", meta.group(1))) if meta else set()
        used = set(re.findall(r"phase\('([^']+)'\)", src)) | set(re.findall(r"phase:\s*'([^']+)'", src))
        if phases and not used <= phases:
            print(f"FAIL {name}: phase titles {sorted(used - phases)} are not declared in meta.phases")
            failures += 1

    print(f"{len(LESSONS)} lessons, {len(scripts)} workflow scripts checked, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
