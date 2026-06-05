"""
moveit.launch.py — MoveIt2 Fake Controller (경로계획 검증용)
"""

import os
import yaml
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

DOCS = os.path.expanduser('~/Documents')

URDF_FILE             = os.path.join(DOCS, '5dof_arm.urdf')
SRDF_FILE             = os.path.join(DOCS, '5dof_arm.srdf')
KINEMATICS_FILE       = os.path.join(DOCS, 'kinematics.yaml')
JOINT_LIMITS_FILE     = os.path.join(DOCS, 'joint_limits.yaml')
FAKE_CONTROLLERS_FILE = os.path.join(DOCS, 'fake_controllers.yaml')


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

    # ── move_group 노드 ───────────────────────────────────────────
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'robot_description_semantic': robot_description_semantic},
            {'robot_description_kinematics': kinematics},
            joint_limits,
            planning_pipeline_params,
            FAKE_CONTROLLERS_FILE,          # ← yaml 경로 직접 전달 (list-of-dicts 대응)
            trajectory_execution_params,
            planning_scene_monitor_params,
            {'use_sim_time': False},
        ],
    )

    # ── robot_state_publisher ─────────────────────────────────────
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': False},
        ],
    )

    # ── joint_state_publisher_gui ─────────────────────────────────
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
    )

    # ── RViz ─────────────────────────────────────────────────────
    rviz_config = os.path.join(DOCS, '5dof_arm_moveit.rviz')
    rviz_args = ['-d', rviz_config] if os.path.exists(rviz_config) else []

    rviz_node = TimerAction(
        period=5.0,
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
                    {'use_sim_time': False},
                ],
            )
        ]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        move_group_node,
        rviz_node,
    ])
