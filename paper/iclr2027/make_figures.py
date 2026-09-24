#!/usr/bin/env python3
"""Compatibility entry point for the current paper's exact-data renderer."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('make_paper_figures.py')), run_name='__main__')
