"""
gazebo_effort.launch.py — Gazebo + position/effort 전환 (MoveIt 없음)

실행:
  ros2 launch arm_5dof_effort gazebo_effort.launch.py

전환:
  ros2 run arm_5dof_effort switch_to_effort.py
  ros2 run arm_5dof_effort switch_to_position.py
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_arm = get_package_share_directory('arm_5dof')
    urdf_file = os.path.join(pkg_arm, 'urdf', '5dof_arm.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Gazebo는 package:// 를 직접 못 읽으므로 절대경로로 치환
    spawn_urdf = '/tmp/5dof_arm_gazebo.urdf'
    with open(spawn_urdf, 'w') as f:
        f.write(robot_description.replace('package://arm_5dof', pkg_arm))

    # ── 1. robot_state_publisher ──────────────────────────────────
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True},
        ],
    )

    # ── 2. Gazebo ─────────────────────────────────────────────────
    gazebo = ExecuteProcess(
        cmd=['ros2', 'launch', 'ros_gz_sim', 'gz_sim.launch.py',
             'gz_args:=-r empty.sdf'],
        output='screen',
    )

    # ── 3. 로봇 spawn (5초 후) ────────────────────────────────────
    spawn_robot = TimerAction(
        period=5.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', '5dof_arm', '-file', spawn_urdf,
                       '-x', '0', '-y', '0', '-z', '0'],
            output='screen',
        )],
    )

    # ── 4. Clock bridge (8초 후) ──────────────────────────────────
    clock_bridge = TimerAction(
        period=8.0,
        actions=[Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen',
        )],
    )

    # ── 5. 컨트롤러 spawn (15초 후) ───────────────────────────────
    #   - joint_state_broadcaster : 항상 활성
    #   - arm_controller          : 활성 (position 모드로 시작)
    #   - gravity_comp_controller : 비활성으로 로드만 (--inactive)
    spawn_controllers = TimerAction(
        period=15.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'run', 'controller_manager', 'spawner',
                     'joint_state_broadcaster'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'run', 'controller_manager', 'spawner',
                     'arm_controller'],
                output='screen',
            ),
            ExecuteProcess(
                cmd=['ros2', 'run', 'controller_manager', 'spawner',
                     '--inactive', 'gravity_comp_controller'],
                output='screen',
            ),
        ],
    )

    # ── 6. gravity_comp_node (17초 후) ───────────────────────────
    #   컨트롤러가 비활성이어도 노드는 켜 두면 됨.
    #   컨트롤러 활성화 즉시 토크 명령이 전달되기 시작함.
    gravity_comp_node = TimerAction(
        period=17.0,
        actions=[Node(
            package='arm_5dof_effort',
            executable='gravity_comp_node.py',
            output='screen',
        )],
    )

    # ── 7. RViz (18초 후) ─────────────────────────────────────────
    rviz = TimerAction(
        period=18.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'use_sim_time': True},
            ],
        )],
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_robot,
        clock_bridge,
        spawn_controllers,
        gravity_comp_node,
        rviz,
    ])
