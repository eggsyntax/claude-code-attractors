#!/bin/bash
cd /tmp/cc-exp/run_2026-01-18_12-48-41/output
python3 -m pytest test_cellular_automaton.py -v
