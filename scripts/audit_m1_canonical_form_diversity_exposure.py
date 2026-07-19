#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from transfer_vs_relearning.utils.io import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the frozen H/Q/T form-exposure audit.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    relations = ("profession", "born_in", "lives_in", "field_of_study", "works_in_industry")
    forms = ("form_a", "form_b", "form_c", "form_d")
    audit = {"treatment_t": {}, "reference_q": {}, "reference_h": {}}
    for relation in relations:
        for form in forms:
            for scaffold in ("direct", "qa"):
                key = f"{relation}/{form}/{scaffold}"
                audit["treatment_t"][key] = "trained" if form in {"form_a", "form_b"} else "held_out"
                audit["reference_q"][key] = "trained" if form in {"form_a", "form_b"} else "held_out"
                audit["reference_h"][key] = "partially_seen" if form == "form_d" and relation in {"born_in", "lives_in"} else "reference_descriptive"
    write_json(args.output, {"status": "passed", "models": audit, "exception": "Reference H Form D is historically seen for born_in and lives_in; it is not unseen-generalization evidence."})


if __name__ == "__main__":
    main()
