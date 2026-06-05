# arm_5dof

[English](README.md) | **한국어**

**ROS 2**, **MoveIt 2**, **Gazebo**(새 Gazebo / `ros_gz` 스택)로 만든 5자유도
매니퓰레이터 시뮬레이션입니다. 로봇 모델, MoveIt 설정, 그리고 팔을 시각화하고
모션을 계획하고 Gazebo에서 실행하는 launch 파일이 들어 있습니다.

> ⚠️ **ROS 2 디스트로:** 사용하는 디스트로(예: Humble / Jazzy)를 확인해 채워넣으세요.
> 이 패키지는 `ros_gz`와 `gz_ros2_control`을 통해 새 Gazebo(`gz-sim`) 스택을 대상으로 합니다.

## 패키지 구조

```
arm_5dof/
├── urdf/        # 로봇 모델 (5dof_arm.urdf)
├── meshes/      # 각 링크의 STL 메시
├── config/      # SRDF, RViz, MoveIt YAML 설정
├── launch/      # launch 파일 (아래 참고)
├── scripts/     # 보조 스크립트 (조인트 슬라이더, 상태 릴레이)
├── package.xml
└── CMakeLists.txt
```

## 의존성

- ROS 2 (디스트로 확인 필요)
- MoveIt 2 (`moveit_ros_move_group`)
- 새 Gazebo + `ros_gz` (`ros_gz_sim`, `ros_gz_bridge`)
- `gz_ros2_control`, `controller_manager`
- `robot_state_publisher`, `joint_state_publisher_gui`, `rviz2`

rosdep으로 ROS 의존성 설치:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

## 빌드

```bash
cd ~/ros2_ws/src
git clone git@github.com:Wjjajja/arm_5dof.git
cd ~/ros2_ws
colcon build --packages-select arm_5dof
source install/setup.bash
```

## 실행

**Gazebo에 표시 + 조인트 슬라이더:**

```bash
ros2 launch arm_5dof display.launch.py
```

**MoveIt 2 fake 컨트롤러 (모션 계획만):**

```bash
ros2 launch arm_5dof moveit.launch.py
```

**MoveIt 2 + Gazebo (전체 시뮬레이션):**

```bash
ros2 launch arm_5dof moveit_gazebo.launch.py
```

## 참고

- URDF의 메시·컨트롤러 경로는 `package://arm_5dof/...` 형식이라 어느 워크스페이스에서도
  동작합니다.
- Gazebo는 실제 파일 경로가 필요하므로, Gazebo launch 파일은 `package://`를 실제 경로로
  치환한 임시 URDF를 `/tmp`에 만들어 사용합니다.
