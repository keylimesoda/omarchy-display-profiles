# Reproduce the preview

```bash
./demo/run /tmp/display-profiles-preview.png
```

Run on an unlocked Omarchy 4 Quattro desktop, with no installed plugin using this companion’s ID. The focused monitor must use transform 0 and scale 1. Python 3 and Omarchy’s normal shell, Hyprland and grim commands are required. Run only when you consent to a brief shell restart and an empty-workspace switch.

The harness backs up shell configuration and cursor/workspace state in `~/.local/state/display-profiles-demo`, refuses stale recovery data, and creates collision-resistant runtime storage. It records a temporary capture copy of the real menu, injecting `monitor-state.py` with committed fictional display data. Hardware/settings actions and the live editor launcher are inert in this copy only. A temporary IPC geometry method exposes the exact card rectangle.

It uses the existing single desktop shell, waits for the fixture read marker and matching IPC state, and crops precisely to the menu card. No user desktop, account information or profile data is captured. The 140 ms card fade is allowed to finish after machine-readable readiness.

A `finally` cleanup and signal handlers restore the shell configuration, plugin path, workspace and cursor, and restart the normal shell. The original configuration is checked byte for byte. If restoration fails, recovery paths are retained and printed. Do not delete a stale recovery directory until its backup has been reconciled with your current desktop.

The root preview was captured this way on Omarchy `4.0.4-1`, x86_64. It demonstrates the hosted menu, not physical monitor-changing or preview-recovery testing.
