from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

INK = HexColor("#111827")
GRID = HexColor("#D1D5DB")
COLORS = {"M1": HexColor("#6B7280"), "M2-A": HexColor("#2563A6"), "M2-B": HexColor("#D97706")}


def load_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def text(c: canvas.Canvas, x: float, y: float, value: str, size: float = 7.5, anchor: str = "start") -> None:
    c.setFillColor(INK)
    c.setFont("Helvetica", size)
    if anchor == "middle":
        c.drawCentredString(x, y, value)
    elif anchor == "end":
        c.drawRightString(x, y, value)
    else:
        c.drawString(x, y, value)


def headline_chart() -> None:
    rows = load_csv("headline_state_accuracy.csv")
    width, height = 7.15 * inch, 2.75 * inch
    out = FIG / "headline_state_accuracy.pdf"
    c = canvas.Canvas(str(out), pagesize=(width, height))
    top, bottom = height - 30, 28
    panel_gap = 25
    panel_width = (width - 58 - panel_gap) / 2
    lefts = [46, 46 + panel_width + panel_gap]
    plot_height = top - bottom
    directions = [("en_to_en", "EN-to-EN"), ("tr_to_en", "TR-to-EN"), ("tr_to_tr", "TR-to-TR")]
    states = ["M1", "M2-A", "M2-B"]

    for x, state in zip([width / 2 - 65, width / 2, width / 2 + 65], states):
        c.setFillColor(COLORS[state])
        c.rect(x - 17, height - 14, 10, 6, fill=1, stroke=0)
        text(c, x - 3, height - 15, state, size=7.2)

    for panel_index, seed in enumerate(["42", "43"]):
        left = lefts[panel_index]
        subset = {row["state"]: row for row in rows if row["seed"] == seed}
        for tick in [0, 20, 40, 60, 80, 100]:
            y = bottom + (tick / 105) * plot_height
            c.setStrokeColor(GRID)
            c.setLineWidth(0.35)
            c.line(left, y, left + panel_width, y)
            if panel_index == 0:
                text(c, left - 6, y - 2.5, str(tick), size=6.4, anchor="end")
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.line(left, bottom, left, top)
        c.line(left, bottom, left + panel_width, bottom)
        text(c, left + panel_width / 2, top + 7, f"Seed {seed}", size=8.5, anchor="middle")

        group_width = panel_width / 3
        bar_width = group_width * 0.22
        for group_index, (column, direction_label) in enumerate(directions):
            center = left + group_width * (group_index + 0.5)
            text(c, center, 15, direction_label, size=7.2, anchor="middle")
            for state_index, state in enumerate(states):
                value = float(subset[state][column])
                x = center + (state_index - 1) * bar_width * 1.1 - bar_width / 2
                bar_height = (value / 105) * plot_height
                c.setFillColor(COLORS[state])
                c.rect(x, bottom, bar_width, bar_height, fill=1, stroke=0)
                label_y = bottom + bar_height + 3
                text(c, x + bar_width / 2, label_y, f"{value:.1f}", size=5.9, anchor="middle")
    c.save()


def effects_chart() -> None:
    rows = load_csv("primary_effects.csv")
    width, height = 4.1 * inch, 2.6 * inch
    out = FIG / "primary_effects.pdf"
    c = canvas.Canvas(str(out), pagesize=(width, height))
    left, right, bottom, top = 142, width - 13, 30, height - 18
    xmin, xmax = -1.1, 2.8
    labels = [
        "Seed 42: arm diff. (descriptive)",
        "Seed 43: arm diff. (descriptive)",
        "Seed 42: Branch interaction (primary)",
        "Seed 43: Branch interaction (primary)",
    ]
    colors = [COLORS["M1"], COLORS["M1"], COLORS["M2-A"], COLORS["M2-A"]]
    ys = [top - i * ((top - bottom) / 3) for i in range(4)]

    def xmap(value: float) -> float:
        return left + (value - xmin) / (xmax - xmin) * (right - left)

    for tick in [-1, 0, 1, 2]:
        x = xmap(tick)
        c.setStrokeColor(INK if tick == 0 else GRID)
        c.setDash(3, 2) if tick == 0 else c.setDash()
        c.setLineWidth(0.55 if tick == 0 else 0.35)
        c.line(x, bottom - 2, x, top + 4)
        c.setDash()
        text(c, x, 17, str(tick), size=6.6, anchor="middle")

    for y, row, label, color in zip(ys, rows, labels, colors):
        estimate = float(row["estimate_pp"])
        low = float(row["ci_low_pp"])
        high = float(row["ci_high_pp"])
        text(c, left - 7, y - 2.5, label, size=6.3, anchor="end")
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.2)
        c.line(xmap(low), y, xmap(high), y)
        c.line(xmap(low), y - 3, xmap(low), y + 3)
        c.line(xmap(high), y - 3, xmap(high), y + 3)
        c.circle(xmap(estimate), y, 2.6, fill=1, stroke=0)

    text(c, (left + right) / 2, 4, "TR-to-EN change (pp; 95% subject-bootstrap CI)", size=6.7, anchor="middle")
    c.save()


if __name__ == "__main__":
    headline_chart()
    effects_chart()
    print(FIG / "headline_state_accuracy.pdf")
    print(FIG / "primary_effects.pdf")
