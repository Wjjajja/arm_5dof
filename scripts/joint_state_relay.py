#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateRelay(Node):
    def __init__(self):
        super().__init__('joint_state_relay')
        self.sub = self.create_subscription(
            JointState, '/joint_states', self.callback, 10)
        self.pub = self.create_publisher(
            JointState, '/joint_states_relay', 10)

    def callback(self, msg):
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = JointStateRelay()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
