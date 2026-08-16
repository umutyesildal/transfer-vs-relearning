#!/usr/bin/env python3
"""Generic user-facing alias for the preserved single-model M0 controller."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).with_name("run_m0_olmo_evaluation.py")),
    run_name="__main__",
)
