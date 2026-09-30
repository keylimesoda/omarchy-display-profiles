#!/usr/bin/env python3
"""Capture the real hosted menu with an explicitly injected fictional state CLI."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ID = json.loads((ROOT / 'manifest.json').read_text())['id']
CONFIG = Path.home() / '.config/omarchy/shell.json'
TARGET = CONFIG.parent / 'plugins' / PLUGIN_ID
RECOVERY = Path.home() / '.local/state/display-profiles-demo'


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()


def query(*args):
    return json.loads(run(*args))


def ipc(*args):
    return run('omarchy-shell', *args)


def wait_for(probe, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = probe()
            if value:
                return value
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
        time.sleep(.1)
    raise RuntimeError('Timed out waiting for shell/fixture readiness')


def stop_signal(signum, frame):
    raise RuntimeError(f'Capture interrupted by signal {signum}')


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'preview.png').resolve()
    for command in ('omarchy-shell', 'omarchy-restart-shell', 'hyprctl', 'grim', 'python3'):
        if not shutil.which(command):
            raise RuntimeError(f'Missing {command}')
    if subprocess.run(['omarchy-hyprland-session-locked'], capture_output=True).returncode == 0:
        raise RuntimeError('Refusing a locked session')
    if not CONFIG.is_file() or TARGET.exists() or TARGET.is_symlink() or RECOVERY.exists():
        raise RuntimeError('Missing shell config, existing candidate installation, or stale recovery directory; resolve it first')
    monitors = query('hyprctl', '-j', 'monitors')
    monitor = next(m for m in monitors if m.get('focused'))
    if monitor.get('transform') != 0 or monitor.get('scale') != 1:
        raise RuntimeError('Capture requires the focused monitor at transform 0 and scale 1')
    workspace = query('hyprctl', '-j', 'activeworkspace')['id']
    used = {w['id'] for w in query('hyprctl', '-j', 'workspaces')}
    empty_workspace = next(w for w in range(90, 100) if w not in used)
    cursor = query('hyprctl', '-j', 'cursorpos')
    original = CONFIG.read_bytes()
    RECOVERY.mkdir(parents=True, exist_ok=False)
    (RECOVERY / 'shell.json').write_bytes(original)
    (RECOVERY / 'session.json').write_text(json.dumps({'workspace': workspace, 'cursor': cursor, 'target': str(TARGET)}))
    runtime = Path(tempfile.mkdtemp(prefix='display-profiles-demo-', dir=os.environ.get('XDG_RUNTIME_DIR', '/tmp')))
    staged = None
    installed = False
    changed = False
    restored = False
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, stop_signal)
    try:
        staged = Path(tempfile.mkdtemp(prefix='.display-profiles-demo-', dir=TARGET.parent))
        for name in ('manifest.json', 'Panel.qml', 'Model.js'):
            shutil.copy2(ROOT / name, staged / name)
        command = ['python3', str(ROOT / 'demo/monitor-state.py'), str(ROOT / 'demo/fixtures/displays.json'), str(runtime / 'fixture-read')]
        qml = (staged / 'Panel.qml').read_text()
        qml = qml.replace('command: ["omarchy-monitor-state"]', 'command: ' + json.dumps(command))
        # The capture-only copy cannot change hardware/settings or open a live editor.
        for signature in ('openLayouts()', 'setBrightness(value)', 'toggleDisplay(name, enabled)', 'setScale(scale)', 'setTextSize(px)'):
            qml = qml.replace('function ' + signature + ' {', 'function ' + signature + ' { return;')
        geometry = '''function demoGeometry(): string { return JSON.stringify({open: root.opened, x: panel.cardOrigin.x, y: panel.cardOrigin.y, screen: panel.screen.name, width: panel.contentWidth, height: panel.contentHeight}) }'''
        qml = qml.replace('function state(): string { return root.stateIpc() }', 'function state(): string { return root.stateIpc() }\n    ' + geometry)
        (staged / 'Panel.qml').write_text(qml)
        staged.rename(TARGET)
        installed = True
        # Only this widget appears in the capture bar. Other user configuration is backed up.
        config = {'version': 1, 'bar': {'position': 'top', 'layout': {'left': [], 'center': [], 'right': [{'id': PLUGIN_ID}]}}, 'plugins': [], 'idle': {'lock': 3600, 'screensaver': 3600}}
        changed = True
        CONFIG.write_text(json.dumps(config, indent=2) + '\n')
        run('omarchy-restart-shell')
        wait_for(lambda: any(p['id'] == PLUGIN_ID and p['enabled'] for p in query('omarchy-shell', 'shell', 'listPlugins')))
        run('hyprctl', 'dispatch', f'hl.dsp.focus({{workspace="{empty_workspace}"}})' )
        run('hyprctl', 'dispatch', 'hl.dsp.cursor.move({x=%d, y=%d})' % (monitor["x"] + 100, monitor["y"] + 100))
        ipc('shell', 'summon', PLUGIN_ID, '{}')
        def ready():
            state = query('omarchy-shell', 'omarchy.monitor', 'state')
            return state.get('focusedMonitor') == 'DP-1' and len(state.get('displays', [])) == 2 and (runtime / 'fixture-read').is_file()
        wait_for(ready)
        geometry = wait_for(lambda: (g if (g := query('omarchy-shell', 'omarchy.monitor', 'demoGeometry')).get('open') and g['width'] > 0 else None))
        # The card's opacity animation is 140 ms; readiness already proves fixture state.
        time.sleep(.25)
        screen = next(m for m in monitors if m['name'] == geometry['screen'])
        rect = f'{round(geometry["x"] + screen["x"])},{round(geometry["y"] + screen["y"])} {round(geometry["width"])}x{round(geometry["height"])}'
        run('grim', '-g', rect, str(output))
        print(f'Captured hosted fictional-data menu: {output}')
    finally:
        try:
            if changed:
                try:
                    ipc('shell', 'hide', PLUGIN_ID)
                except subprocess.SubprocessError:
                    pass
                CONFIG.write_bytes(original)
            if staged is not None and staged.exists():
                shutil.rmtree(staged)
            if installed:
                # TARGET is one validated ID created by this invocation, never an ambiguous path.
                shutil.rmtree(TARGET)
            run('omarchy-restart-shell')
            wait_for(lambda: ipc('shell', 'ping') == 'ok')
            run('hyprctl', 'dispatch', f'hl.dsp.focus({{workspace="{workspace}"}})' )
            run('hyprctl', 'dispatch', 'hl.dsp.cursor.move({x=%d, y=%d})' % (cursor["x"], cursor["y"]))
            if CONFIG.read_bytes() != original or TARGET.exists():
                raise RuntimeError('Configuration or plugin restoration mismatch')
            restored = True
        finally:
            if restored:
                shutil.rmtree(runtime)
                shutil.rmtree(RECOVERY)
                print('Restored configuration, plugin installation, workspace and cursor.')
            else:
                print(f'Restoration needs attention. Backups: {RECOVERY}; runtime: {runtime}', file=sys.stderr)


if __name__ == '__main__':
    main()
