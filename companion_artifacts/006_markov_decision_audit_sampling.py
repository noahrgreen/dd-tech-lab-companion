#!/usr/bin/env python3
"""Compatibility entrypoint for 006_markov_decision_audit_sampling.py."""
from __future__ import annotations

import runpy
from pathlib import Path

TARGET = (Path(__file__).resolve().parent / '../stochastic_markov/companion_artifacts/006_markov_decision_audit_sampling.py').resolve()

if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
