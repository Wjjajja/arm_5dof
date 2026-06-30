#!/usr/bin/env python3
"""
/joint_states 를 읽어 KDL로 G(q) 를 계산하고
/gravity_comp_controller/commands 에 effort 토크를 publish 한다.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

import PyKDL
from urdf_parser_py.urdf import URDF
from kdl_parser_py.urdf import treeFromUrdfModel
from ament_index_python.packages import get_package_share_directory
import os


JOINT_NAMES = ['joint0', 'joint1', 'joint2', 'joint3', 'joint4']
BASE_LINK   = 'base_link'
TIP_LINK    = 'link4'


class GravityCompNode(Node):
    def __init__(self):
        super().__init__('gravity_comp_node')

        urdf_path = os.path.join(
            get_package_share_directory('arm_5dof'), 'urdf', '5dof_arm.urdf')

        robot = URDF.from_xml_file(urdf_path)
        ok, tree = treeFromUrdfModel(robot)
        if not ok:
            self.get_logger().error('KDL tree parse failed')
            raise RuntimeError('KDL tree parse failed')

        chain = tree.getChain(BASE_LINK, TIP_LINK)
        self.n = chain.getNrOfJoints()

        self.dyn = PyKDL.ChainDynParam(chain, PyKDL.Vector(0, 0, -9.81))
        self.q   = PyKDL.JntArray(self.n)
        self.g   = PyKDL.JntArray(self.n)

        self.pub = self.create_publisher(
            Float64MultiArray, '/gravity_comp_controller/commands', 10)
        self.create_subscription(
            JointState, '/joint_states', self._cb, 10)

        self.get_logger().info('gravity_comp_node ready')

    def _cb(self, msg: JointState):
        name_to_pos = dict(zip(msg.name, msg.position))
        for i, name in enumerate(JOINT_NAMES):
            if name in name_to_pos:
                self.q[i] = name_to_pos[name]

        self.dyn.JntToGravity(self.q, self.g)

        cmd = Float64MultiArray()
        cmd.data = [self.g[i] for i in range(self.n)]
        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = GravityCompNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
