cmake_minimum_required(VERSION 3.8)
project(arm_5dof)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  urdf
  meshes
  config
  launch
  scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
