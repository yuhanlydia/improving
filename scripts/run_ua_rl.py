#!/usr/bin/env python3
"""Run the optional, explicitly judged UA-RL (adapted) comparison."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from improving.ua_rl import main

if __name__ == '__main__':
    main()
