#!/usr/bin/env python3
"""Compatibility entrypoint for 004_mixture_round_tripping.py."""
from __future__ import annotations

import runpy
from pathlib import Path

TARGET = (Path(__file__).resolve().parent / 'companion_artifacts/004_mixture_round_tripping.py').resolve()

if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
