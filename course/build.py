"""Build the single-page course into dist/scaling-agents.html.

The page embeds a zip of ../kestrel-starter so the download button and the
repo always ship the same starter.
"""
import base64
import io
import os
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "kestrel-starter"
SKIP_DIRS = {"node_modules", ".venv", "__pycache__", ".pytest_cache", ".git"}


def starter_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(STARTER):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                path = Path(root) / name
                arc = Path("kestrel-starter") / path.relative_to(STARTER)
                info = zipfile.ZipInfo(str(arc), date_time=(2026, 1, 1, 0, 0, 0))
                info.external_attr = (0o100755 if os.access(path, os.X_OK) else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
    return buf.getvalue()


def read(name: str) -> str:
    return (HERE / name).read_text()


def build() -> Path:
    from ladder import SVG

    lessons = []
    for path in sorted((HERE / "lessons").glob("lesson-*.html")):
        section = path.read_text().strip()
        lessons.append(section.replace('<section class="lesson"', '<section class="lesson view" data-view hidden', 1))
    page = (
        read("template.html")
        .replace("{{CSS}}", read("shell.css"))
        .replace("{{JS}}", read("shell.js"))
        .replace("{{HOME}}", read("home.html").replace("{{LADDER}}", SVG))
        .replace("{{LESSONS}}", "\n".join(lessons))
        .replace("{{REFERENCE}}", read("reference.html").replace("data-view>", "data-view hidden>", 1))
        .replace("{{ZIP}}", base64.b64encode(starter_zip()).decode())
    )
    out = HERE / "dist" / "scaling-agents.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)
    return out


if __name__ == "__main__":
    out = build()
    print(f"built {out.relative_to(HERE)} ({out.stat().st_size // 1024} KB)")
