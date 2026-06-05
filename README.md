# arm_5dof

**English** | [한국어](README.ko.md)

A 5-DOF manipulator simulation built with **ROS 2**, **MoveIt 2**, and **Gazebo**
(new Gazebo / `ros_gz` stack). The package contains the robot model, MoveIt
configuration, and launch files to visualize the arm, plan motions, and run it
in Gazebo.

> ⚠️ **ROS 2 distro:** confirm and fill in your distro (e.g. Humble / Jazzy).
> This package targets the new Gazebo (`gz-sim`) stack via `ros_gz` and
> `gz_ros2_control`.

## Package layout

```
arm_5dof/
├── urdf/        # robot model (5dof_arm.urdf)
├── meshes/      # STL meshes for each link
├── config/      # SRDF, RViz, and MoveIt YAML configs
├── launch/      # launch files (see below)
├── scripts/     # helper scripts (joint slider, state relay)
├── package.xml
└── CMakeLists.txt
```

## Dependencies

- ROS 2 (confirm your distro)
- MoveIt 2 (`moveit_ros_move_group`)
- New Gazebo + `ros_gz` (`ros_gz_sim`, `ros_gz_bridge`)
- `gz_ros2_control`, `controller_manager`
- `robot_state_publisher`, `joint_state_publisher_gui`, `rviz2`

Install ROS dependencies with rosdep:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
cd ~/ros2_ws/src
git clone git@github.com:Wjjajja/arm_5dof.git
cd ~/ros2_ws
colcon build --packages-select arm_5dof
source install/setup.bash
```

## Run

**Display in Gazebo with a joint slider:**

```bash
ros2 launch arm_5dof display.launch.py
```

**MoveIt 2 with fake controllers (motion planning only):**

```bash
ros2 launch arm_5dof moveit.launch.py
```

**MoveIt 2 + Gazebo (full simulation):**

```bash
ros2 launch arm_5dof moveit_gazebo.launch.py
```

## Notes

- Mesh and controller paths in the URDF use `package://arm_5dof/...` so the
  package works from any workspace.
- Gazebo launch files write a temporary URDF to `/tmp` with `package://`
  resolved to real file paths, since Gazebo needs filesystem paths.
