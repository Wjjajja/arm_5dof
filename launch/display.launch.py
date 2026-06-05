from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('arm_5dof')
    urdf_file = os.path.join(pkg, 'urdf', '5dof_arm.urdf')
    rviz_file = os.path.join(pkg, 'config', '5dof_arm.rviz')
    slider_file = os.path.join(pkg, 'scripts', 'joint_slider.py')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    # Gazebo needs real file paths, so make a copy with package:// resolved
    spawn_urdf = '/tmp/5dof_arm_gazebo.urdf'
    with open(spawn_urdf, 'w') as f:
        f.write(robot_description.replace('package://arm_5dof', pkg))
    return LaunchDescription([
        # robot_state_publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),
        # Gazebo
        ExecuteProcess(
            cmd=['ros2', 'launch', 'ros_gz_sim', 'gz_sim.launch.py',
                 'gz_args:=-r empty.sdf'],
            output='screen'
        ),
        # 로봇 spawn
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    arguments=[
                        '-name', '5dof_arm',
                        '-file', spawn_urdf,
                        '-x', '0', '-y', '0', '-z', '0'
                    ],
                    output='screen'
                )
            ]
        ),
        # 컨트롤러 로드
        TimerAction(
            period=15.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'controller_manager', 'spawner',
                         'joint_state_broadcaster'],
                    output='screen'
                ),
                ExecuteProcess(
                    cmd=['ros2', 'run', 'controller_manager', 'spawner',
                         'arm_controller'],
                    output='screen'
                ),
            ]
        ),
        # 슬라이더 GUI
        TimerAction(
            period=17.0,
            actions=[
                ExecuteProcess(
                    cmd=['python3', slider_file],
                    output='screen'
                )
            ]
        ),
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_file],
        ),
    ])
