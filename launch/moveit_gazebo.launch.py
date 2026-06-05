"""
moveit_gazebo.launch.py — MoveIt2 + Gazebo Ignition 통합 launch

실행:
  ros2 launch ~/Documents/moveit_gazebo.launch.py

타임라인:
  0s   Gazebo + robot_state_publisher
  5s   로봇 spawn
  8s   Clock bridge
  15s  Controller spawner (joint_state_broadcaster + arm_controller)
  20s  move_group (OMPL)
  25s  RViz (MoveIt plugin)
"""

import os
import yaml
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

DOCS = os.path.expanduser('~/Documents')

URDF_FILE             = os.path.join(DOCS, '5dof_arm.urdf')
SRDF_FILE             = os.path.join(DOCS, '5dof_arm.srdf')
KINEMATICS_FILE       = os.path.join(DOCS, 'kinematics.yaml')
JOINT_LIMITS_FILE     = os.path.join(DOCS, 'joint_limits.yaml')
MOVEIT_CONTROLLERS    = os.path.join(DOCS, 'moveit_controllers.yaml')


def load_file(path):
    with open(path, 'r') as f:
        return f.read()


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def generate_launch_description():

    robot_description_content  = load_file(URDF_FILE)
    robot_description_semantic = load_file(SRDF_FILE)
    kinematics                 = load_yaml(KINEMATICS_FILE)
    joint_limits               = load_yaml(JOINT_LIMITS_FILE)

    # ── OMPL planning pipeline (확인된 경로: move_group.planning_plugin) ──
    planning_pipeline_params = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': ' '.join([
                'default_planner_request_adapters/AddTimeOptimalParameterization',
                'default_planner_request_adapters/ResolveConstraintFrames',
                'default_planner_request_adapters/FixWorkspaceBounds',
                'default_planner_request_adapters/FixStartStateBounds',
                'default_planner_request_adapters/FixStartStateCollision',
                'default_planner_request_adapters/FixStartStatePathConstraints',
            ]),
            'start_state_max_bounds_error': 0.1,
        }
    }

    trajectory_execution_params = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 2.0,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    planning_scene_monitor_params = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
    }

    # ═══════════════════════════════════════════════════════════════
    # 1. robot_state_publisher
    # ═══════════════════════════════════════════════════════════════
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': True},
        ],
    )

    # ═══════════════════════════════════════════════════════════════
    # 2. Gazebo Ignition
    # ═══════════════════════════════════════════════════════════════
    gazebo = ExecuteProcess(
        cmd=['ros2', 'launch', 'ros_gz_sim', 'gz_sim.launch.py',
             'gz_args:=-r empty.sdf'],
        output='screen',
    )

    # ═══════════════════════════════════════════════════════════════
    # 3. 로봇 spawn (5초 후)
    # ═══════════════════════════════════════════════════════════════
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', '5dof_arm',
                    '-file', URDF_FILE,
                    '-x', '0', '-y', '0', '-z', '0',
                ],
                output='screen',
            )
        ],
    )

    # ═══════════════════════════════════════════════════════════════
    # 4. Clock bridge (8초 후)
    # ═══════════════════════════════════════════════════════════════
    clock_bridge = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
                output='screen',
            )
        ],
    )

    # ═══════════════════════════════════════════════════════════════
    # 5. Controller spawner (15초 후)
    # ═══════════════════════════════════════════════════════════════
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
        ],
    )

    # ═══════════════════════════════════════════════════════════════
    # 6. MoveIt2 move_group (20초 후 — controller 준비 후)
    # ═══════════════════════════════════════════════════════════════
    move_group_node = TimerAction(
        period=20.0,
        actions=[
            Node(
                package='moveit_ros_move_group',
                executable='move_group',
                output='screen',
                parameters=[
                    {'robot_description': robot_description_content},
                    {'robot_description_semantic': robot_description_semantic},
                    {'robot_description_kinematics': kinematics},
                    joint_limits,
                    planning_pipeline_params,
                    MOVEIT_CONTROLLERS,         # yaml 경로 직접 전달
                    trajectory_execution_params,
                    planning_scene_monitor_params,
                    {'use_sim_time': True},
                ],
            )
        ],
    )

    # ═══════════════════════════════════════════════════════════════
    # 7. RViz with MoveIt (25초 후)
    # ═══════════════════════════════════════════════════════════════
    rviz_config = os.path.join(DOCS, '5dof_arm_moveit.rviz')
    rviz_args = ['-d', rviz_config] if os.path.exists(rviz_config) else []

    rviz_node = TimerAction(
        period=25.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                output='screen',
                arguments=rviz_args,
                parameters=[
                    {'robot_description': robot_description_content},
                    {'robot_description_semantic': robot_description_semantic},
                    {'robot_description_kinematics': kinematics},
                    {'use_sim_time': True},
                ],
            )
        ],
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo,
        spawn_robot,
        clock_bridge,
        spawn_controllers,
        move_group_node,
        rviz_node,
    ])
