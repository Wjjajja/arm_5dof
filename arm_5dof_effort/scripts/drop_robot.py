#!/usr/bin/env python3
"""토크를 0으로 → 중력에 의해 팔 낙하."""
import subprocess, sys

result = subprocess.run([
    'ros2', 'topic', 'pub', '--once',
    '/gravity_comp/enable',
    'std_msgs/msg/Bool',
    '{data: false}',
])
if result.returncode == 0:
    print('→ 토크 OFF: 팔이 중력에 의해 낙하합니다')
else:
    sys.exit(1)
