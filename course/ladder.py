"""The four team shapes drawn in the course hero: 1, 5, 25 and 100 agents."""

W, H = 720, 250
TOP = 52
out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Four team shapes: one agent in a loop, an orchestrator with four workers, a two-level tree of 25, and a three-level tree of 100">']


def dot(x, y, r, cls):
    out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')


def line(x1, y1, x2, y2):
    out.append(f'<path class="ladder__e" d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}"/>')


cx = 90
out.append(f'<path class="ladder__e" d="M{cx + 14} {TOP + 60} a26 26 0 1 1 -2 -14" style="stroke:var(--accent);stroke-width:1.6"/>')
dot(cx, TOP + 70, 12, "ladder__w")

cx = 270
workers = [cx - 66 + i * 44 for i in range(4)]
for x in workers:
    line(cx, TOP + 30, x, TOP + 110)
for x in workers:
    dot(x, TOP + 110, 9, "ladder__w")
dot(cx, TOP + 30, 12, "ladder__o")

cx = 450
leads = [cx - 63 + i * 42 for i in range(4)]
for lx in leads:
    line(cx, TOP + 14, lx, TOP + 70)
    for j in range(5):
        line(lx, TOP + 70, lx - 14 + j * 7, TOP + 128)
for lx in leads:
    for j in range(5):
        dot(lx - 14 + j * 7, TOP + 128, 3.2, "ladder__w")
    dot(lx, TOP + 70, 6.5, "ladder__c")
dot(cx, TOP + 14, 9, "ladder__o")

cx = 630
leads = [cx - 72 + i * 18 for i in range(9)]
for lx in leads:
    line(cx, TOP + 4, lx, TOP + 60)
for lx in leads:
    for j in range(10):
        dot(lx - 3.5 + (j % 2) * 7, TOP + 86 + (j // 2) * 10, 2.3, "ladder__w")
    out.append(f'<path class="ladder__e" d="M{lx:.1f} {TOP + 60} L{lx:.1f} {TOP + 82}"/>')
    dot(lx, TOP + 60, 4.2, "ladder__c")
dot(cx, TOP + 4, 7, "ladder__o")

for x, n, label in ((90, "1", "ONE AGENT"), (270, "5", "SMALL TEAM"), (450, "25", "SYSTEM"), (630, "100", "SCALE")):
    out.append(f'<text class="ladder__n" x="{x}" y="{H - 36}">{n}</text>')
    out.append(f'<text class="ladder__lbl" x="{x}" y="{H - 14}">{label}</text>')
for x in (180, 360, 540):
    out.append(f'<path class="ladder__e" d="M{x} 30 L{x} {H - 60}" style="stroke-dasharray:3 5"/>')
out.append("</svg>")
SVG = "\n".join(out)
