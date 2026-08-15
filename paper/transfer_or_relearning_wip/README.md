# Transfer or Relearning? — WIP paper

This directory contains the editable LaTeX source, figures, data extracts, bibliography, and internal evidence map for the 9 August 2026 work-in-progress paper.

## Build

From this directory:

```bash
python3 build_figures.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The final reviewed PDF is exported separately to `output/pdf/transfer_or_relearning_wip_20260809.pdf`.

## Scientific status

- Completed result: two-seed Qwen Wikipedia-only 1M-token pilot.
- Frozen decision: `primary_success_criterion_not_met`.
- Prospective literature-first M2-A/M2-B study: unexecuted and blocked by unresolved measurement design/corpus selection.
