#!/usr/bin/env python3
"""gravity compensation (effort) → position 모드 전환."""
import subprocess, sys

result = subprocess.run([
    'ros2', 'control', 'switch_controllers',
    '--deactivate', 'gravity_comp_controller',
    '--activate', 'arm_controller',
    '--strict',
])
if result.returncode == 0:
    print('→ position control 모드')
else:
    sys.exit(1)
