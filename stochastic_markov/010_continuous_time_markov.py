#!/usr/bin/env python3
"""Compatibility entrypoint for 010_continuous_time_markov.py."""
from __future__ import annotations

import runpy
from pathlib import Path

TARGET = (Path(__file__).resolve().parent / 'companion_artifacts/010_continuous_time_markov.py').resolve()

if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
