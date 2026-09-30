#!/usr/bin/env python3
"""Fictional eight-line state source, used only by the capture copy."""
import json
import sys
from pathlib import Path
state = json.loads(Path(sys.argv[1]).read_text())
if len(sys.argv) == 3:
  Path(sys.argv[2]).write_text("fictional-state-loaded\n")
print(state["brightness"])
print(state["internal"])
print(state["external"])
print(state["internal"])
print("")
print(state["focused"])
print(state["scale"])
print(json.dumps(state["displays"], separators=(",", ":")))
