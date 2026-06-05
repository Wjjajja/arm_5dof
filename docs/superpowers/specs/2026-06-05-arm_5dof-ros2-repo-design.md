# arm_5dof — ROS2 패키지 레포 정리 설계

작성일: 2026-06-05

## 1. 목표

진행 중인 **5자유도 매니퓰레이터 시뮬레이션**(ROS2 + MoveIt2 + 새 Gazebo) 작업을,
누구나 클론해서 빌드·실행할 수 있는 **표준 ROS2 패키지** 형태로 정리해 GitHub에 올린다.

성공 기준:
- 표준 ROS2 패키지 디렉토리 구조를 갖춘다.
- 하드코딩된 절대경로가 모두 제거되고, 패키지 상대경로로 대체된다.
- README만 보고 빌드·실행 흐름을 이해할 수 있다.
- GitHub 레포에 커밋 이력과 함께 올라간다.

## 2. 현재 상태 (출발점)

원본: `~/Desktop/urdf/` (flat 디렉토리, 백업으로 보존)

- 로봇 모델: `5dof_arm.urdf`, `5dof_arm.srdf`
- 메시: `base_link.stl`, `link0~4.stl` (6개)
- MoveIt 설정 7개: `kinematics.yaml`, `joint_limits.yaml`, `ompl_planning.yaml`,
  `controllers.yaml`, `moveit_controllers.yaml`, `fake_controllers.yaml`, `move_group_params.yaml`
- launch 3개: `moveit.launch.py`, `moveit_gazebo.launch.py`, `display.launch.py`
- 스크립트 2개: `joint_slider.py`, `joint_state_relay.py`
- 시각화: `5dof_arm.rviz`

**핵심 문제 — 하드코딩된 절대경로:**
- `5dof_arm.urdf`: 메시 12곳이 `file:///home/ubuntu/Documents/<name>.stl`
- `5dof_arm.urdf`: gz_ros2_control 플러그인의 `<parameters>/home/ubuntu/Documents/controllers.yaml</parameters>`
- `display.launch.py`: `~/Documents/5dof_arm.urdf`, `5dof_arm.rviz`, `joint_slider.py`
- `moveit_gazebo.launch.py`: `DOCS = ~/Documents` 기준 다수 파일
- `moveit.launch.py`: (동일 패턴 추정 — 작업 시 확인)

이 경로들 때문에 다른 환경에서는 동작하지 않는다.

## 3. 목표 구조

레포 루트(`arm_5dof/`)가 곧 ROS2 패키지다. 사용자는 이 레포를 `~/ros2_ws/src/`에 클론해 `colcon build` 한다.

```
arm_5dof/
├── package.xml            (신규 — 의존성 명시)
├── CMakeLists.txt         (신규 — ament_cmake, install 규칙)
├── urdf/
│   └── 5dof_arm.urdf      (경로 수정)
├── meshes/
│   └── *.stl              (6개)
├── config/
│   ├── 5dof_arm.srdf
│   ├── 5dof_arm.rviz
│   ├── kinematics.yaml
│   ├── joint_limits.yaml
│   ├── ompl_planning.yaml
│   ├── controllers.yaml
│   ├── moveit_controllers.yaml
│   ├── fake_controllers.yaml
│   └── move_group_params.yaml
├── launch/
│   ├── display.launch.py        (경로 수정)
│   ├── moveit.launch.py         (경로 수정)
│   └── moveit_gazebo.launch.py  (경로 수정)
├── scripts/
│   ├── joint_slider.py
│   └── joint_state_relay.py
├── README.md
├── .gitignore
└── docs/                  (설계 문서 등)
```

라이선스: **현재 미정** — LICENSE 파일은 두지 않는다 (추후 추가 가능).

## 4. 핵심 작업

### 4.1 경로 이식성 수정
- **URDF 메시**: `file:///home/ubuntu/Documents/X.stl` → `package://arm_5dof/meshes/X.stl`
- **URDF 컨트롤러 파라미터**: `/home/ubuntu/Documents/controllers.yaml`
  → launch에서 share 경로로 주입하거나, `package://` 가 불가한 항목이므로
    launch 시점에 `get_package_share_directory()`로 절대경로를 만들어 전달
    (구체 방식은 구현 단계에서 launch 구조 보고 결정)
- **launch 파일**: `~/Documents/...` 및 `DOCS` 기준 경로
  → `from ament_index_python.packages import get_package_share_directory`
    `pkg = get_package_share_directory('arm_5dof')` 기준 경로로 교체

### 4.2 빌드 파일 생성
- `package.xml`: 패키지명 `arm_5dof`, 의존성(`robot_state_publisher`, `ros_gz_sim`,
  `ros_gz_bridge`, `gz_ros2_control`, `moveit_ros_move_group`, `rviz2`, `xacro` 등 실제 참조 기반)
- `CMakeLists.txt`: ament_cmake, `urdf/ meshes/ config/ launch/ scripts/` 를 share에 install,
  Python 스크립트 install

### 4.3 문서화
- `README.md`: 프로젝트 개요(5자유도 팔), 의존성, 빌드(`colcon build`), 실행 명령
  (display / moveit / moveit_gazebo launch), 스크린샷(데스크탑 PNG 활용)
- `.gitignore`: `build/ install/ log/ __pycache__/ *.pyc`

## 5. 디스트로 / 환경

- 스택 단서: `ros_gz_sim`, `ros_gz_bridge`, `gz_ros2_control`,
  플러그인 `gz_ros2_control::GazeboSimROS2ControlPlugin`, `libgz_ros2_control-system.so`
  → **새 Gazebo(gz-sim) 스택**. ROS2 Jazzy(Harmonic) 또는 Humble(Garden+) 계열로 추정.
- 정확한 디스트로는 사용자 확인 필요. README에 "⚠️ 확인 필요" 로 명시하고,
  사용자가 실제 환경값으로 채운다.

## 6. 제약 / 검증 한계 (중요)

- 개발 환경은 **macOS**, 실제 ROS2/Gazebo 실행 환경은 **리눅스**다.
- 따라서 구조 재정리·경로 수정·문서화는 macOS에서 수행하지만,
  **최종 `colcon build` + launch 실작동 검증은 사용자의 리눅스 ROS2 머신에서** 이루어진다.
- 경로 수정의 정확성은 그 머신에서의 빌드/실행으로 최종 확인한다.

## 7. GitHub 반영

- 라이선스 미정 → LICENSE 없이 진행.
- 사용자가 GitHub 웹에서 **빈 레포 `arm_5dof`** 를 생성한다.
- 로컬에서 `git init`(완료) → 정리/커밋 → `git remote add origin git@github.com:Wjjajja/arm_5dof.git`
  → `git push -u origin main`.
- SSH 인증은 검증 완료(`id_ed25519`, 계정 `Wjjajja`).

**커밋 워크플로 (사용자 통제):**
- 모든 커밋은 **제안 → 승인 → 실행** 방식. 클로드가 커밋 단위(파일 묶음)와
  커밋 메시지를 제안하고, 사용자가 승인한 것만 commit 한다.
- push 시점·여부도 사용자가 결정한다.

## 8. 범위 밖 (YAGNI)

- description / moveit_config 패키지 분리 (지금은 단일 패키지로 충분)
- xacro 매크로화, CI, 테스트 코드, 도커 등은 이번 범위에 넣지 않음.
- 원본 `~/Desktop/urdf/` 는 삭제하지 않고 백업으로 보존.
