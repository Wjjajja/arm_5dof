#!/usr/bin/env python3
"""position → gravity compensation (effort) 모드 전환."""
import subprocess, sys

result = subprocess.run([
    'ros2', 'control', 'switch_controllers',
    '--deactivate', 'arm_controller',
    '--activate', 'gravity_comp_controller',
    '--strict',
])
if result.returncode == 0:
    print('→ gravity compensation 모드')
else:
    sys.exit(1)
