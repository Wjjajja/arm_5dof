"""
full_demo.launch.py — MoveIt 위치제어 + 중력보상 effort 제어 + 낙하 데모

시나리오:
  1. (기본) 위치 제어 — RViz/MoveIt으로 자유롭게 자세 변경
  2. (전환) ros2 run arm_5dof_effort switch_to_effort.py
           → 중력보상 토크로 자세 유지
  3. (낙하) ros2 run arm_5dof_effort drop_robot.py
           → 토크 0 → 중력에 의해 팔 낙하
  4. (복귀) ros2 run arm_5dof_effort switch_to_position.py

실행:
  ros2 launch arm_5dof full_demo.launch.py
"""

import os
import yaml
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

PKG = get_package_share_directory('arm_5dof')

URDF_FILE          = os.path.join(PKG, 'urdf', '5dof_arm.urdf')
SRDF_FILE          = os.path.join(PKG, 'config', '5dof_arm.srdf')
KINEMATICS_FILE    = os.path.join(PKG, 'config', 'kinematics.yaml')
JOINT_LIMITS_FILE  = os.path.join(PKG, 'config', 'joint_limits.yaml')
MOVEIT_CONTROLLERS = os.path.join(PKG, 'config', 'moveit_controllers.yaml')


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

    spawn_urdf = '/tmp/5dof_arm_gazebo.urdf'
    with open(spawn_urdf, 'w') as f:
        f.write(robot_description_content.replace('package://arm_5dof', PKG))

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

    # ── 1. robot_state_publisher ──────────────────────────────────
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': True},
        ],
    )

    # ── 2. Gazebo ─────────────────────────────────────────────────
    gazebo = ExecuteProcess(
        cmd=['ros2', 'launch', 'ros_gz_sim', 'gz_sim.launch.py',
             'gz_args:=-r empty.sdf'],
        output='screen',
    )

    # ── 3. 로봇 spawn (5초 후) — 기본 pose는 URDF origin (일직선) ──
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', '5dof_arm',
                    '-file', spawn_urdf,
                    '-x', '0', '-y', '0', '-z', '0',
                ],
                output='screen',
            )
        ],
    )

    # ── 4. Clock bridge (8초 후) ──────────────────────────────────
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

    # ── 5. 컨트롤러 spawn (15초 후) ───────────────────────────────
    #   arm_controller         : 활성 (position, MoveIt용)
    #   gravity_comp_controller: 비활성 로드 (전환 대기)
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

    # ── 6. gravity_comp_node (17초 후) ────────────────────────────
    #   컨트롤러가 비활성이어도 토크 계산은 미리 시작.
    #   /gravity_comp/enable = true(기본)이면 G(q) 발행,
    #   false면 zeros 발행 (→ 팔 낙하).
    gravity_comp_node = TimerAction(
        period=17.0,
        actions=[
            Node(
                package='arm_5dof_effort',
                executable='gravity_comp_node.py',
                output='screen',
            )
        ],
    )

    # ── 7. MoveIt move_group (20초 후) ────────────────────────────
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
                    MOVEIT_CONTROLLERS,
                    trajectory_execution_params,
                    planning_scene_monitor_params,
                    {'use_sim_time': True},
                ],
            )
        ],
    )

    # ── 8. RViz with MoveIt (25초 후) ─────────────────────────────
    rviz_config = os.path.join(PKG, 'config', '5dof_arm_moveit.rviz')
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
        gravity_comp_node,
        move_group_node,
        rviz_node,
    ])
