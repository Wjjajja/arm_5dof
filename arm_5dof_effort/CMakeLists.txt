cmake_minimum_required(VERSION 3.8)
project(arm_5dof_effort)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
  scripts/gravity_comp_node.py
  scripts/switch_to_effort.py
  scripts/switch_to_position.py
  scripts/drop_robot.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
