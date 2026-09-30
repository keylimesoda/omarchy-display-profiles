# Validation

Target: Omarchy `4.0.4-1` Quattro, x86_64, Qt 6 and Quickshell from the installed Omarchy desktop. Two physical displays were available, including one rotated display. Compatibility with older shell contracts and other architectures is untested.

## Checked behavior

- Portable and installed Omarchy manifest validation.
- QML lint using the installed `qs.Ui` and `qs.Commons` imports: no errors; existing dynamic-property warnings remain.
- The hosted menu renders with fictional state through `demo/run`; its capture restores the configuration byte for byte, workspace, cursor and plugin installation.
- The “Layouts & profiles” action opens the existing hidden hyprmoncfg panel from the Display menu; repeated opening and Escape dismissal were exercised on the physical desktop.
- The hyprmoncfg icon can have zero size and opacity while its editor and persistent preview service remain loaded, including after a full shell restart. Keeping the anchor item visible is necessary for the panel to map.

Installation from the public Git repository, update from the initial checkout to the launch-ordering fix, enablement replacing the stock menu, and removal restoring the stock menu were exercised on the live desktop. The prior custom menu and original configuration were restored afterward. Exact source identities are recorded in the release record. This file describes the feature test scope; a source commit ID is recorded externally to avoid referring to its own commit recursively.

The menu action is inherited from the working user-owned Display clone. The separate upstream plugin change passed 161 JavaScript tests and 21 offscreen QML tests. The native Omarchy integration passed 28 focused monitor-model assertions, including unavailable/disabled/service-only editor cases. Those upstream suites cover their own repositories, not certification of this companion.

## Limits

No hardware-changing brightness, scale or display-toggle action was executed during this integration test. Preview keep/revert, hotplug, suspend and other hardware scenarios were not retested for the menu launcher. The backend retry fix is separate and not bundled. No disposable VM or ARM64 checks were run.

Static validation reports process execution and collected-output capabilities in the inherited Display widget. These were reviewed as existing Omarchy monitor commands plus the explicit cross-plugin shell summon. Their results are limited evidence, not a security audit or marketplace approval. Omakit’s additional marketplace-baseline checks were not run because Omakit is not installed; the skill’s strict local validator and current official form were used.
