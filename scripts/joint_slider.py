#!/usr/bin/env python3
"""
5DOF 로봇 팔 관절 슬라이더 GUI
"""
import sys
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import tkinter as tk

class JointSliderGUI(Node):
    def __init__(self):
        super().__init__('joint_slider_gui')
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )
        self.joint_names = ['joint0', 'joint1', 'joint2', 'joint3', 'joint4']
        self.joint_limits = [
            (-3.14159, 3.14159),   # joint0 Roll
            (-1.5708, 1.5708),     # joint1 Pitch
            (-1.5708, 1.5708),     # joint2 Pitch
            (-1.5708, 1.5708),     # joint3 Pitch
            (-3.14159, 3.14159),   # joint4 Roll
        ]
        self.sliders = []
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("5DOF Arm Joint Controller")
        self.root.geometry("500x400")
        self.root.configure(bg='#2b2b2b')

        tk.Label(self.root, text="5DOF Robot Arm Controller",
                 font=("Arial", 14, "bold"),
                 bg='#2b2b2b', fg='white').pack(pady=10)

        joint_labels = ['J0 Roll', 'J1 Pitch', 'J2 Pitch', 'J3 Pitch', 'J4 Roll']

        for i, (label, limits) in enumerate(zip(joint_labels, self.joint_limits)):
            frame = tk.Frame(self.root, bg='#2b2b2b')
            frame.pack(fill='x', padx=20, pady=5)

            tk.Label(frame, text=f"{label}:", width=10,
                     bg='#2b2b2b', fg='white',
                     font=("Arial", 10)).pack(side='left')

            val_label = tk.Label(frame, text="0.00", width=6,
                                  bg='#2b2b2b', fg='#00ff88',
                                  font=("Arial", 10))
            val_label.pack(side='right')

            slider = tk.Scale(
                frame,
                from_=limits[0],
                to=limits[1],
                resolution=0.01,
                orient='horizontal',
                length=300,
                bg='#3c3c3c', fg='white',
                troughcolor='#555555',
                highlightbackground='#2b2b2b',
                command=lambda v, lbl=val_label: lbl.config(text=f"{float(v):.2f}")
            )
            slider.pack(side='left', padx=5)
            self.sliders.append(slider)

        # 버튼 프레임
        btn_frame = tk.Frame(self.root, bg='#2b2b2b')
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Send Command",
                  command=self.send_command,
                  bg='#00aa55', fg='white',
                  font=("Arial", 11, "bold"),
                  padx=15, pady=5).pack(side='left', padx=10)

        tk.Button(btn_frame, text="Reset (All Zero)",
                  command=self.reset_joints,
                  bg='#aa5500', fg='white',
                  font=("Arial", 11, "bold"),
                  padx=15, pady=5).pack(side='left', padx=10)

        self.status_label = tk.Label(self.root, text="Ready",
                                      bg='#2b2b2b', fg='#888888',
                                      font=("Arial", 9))
        self.status_label.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def send_command(self):
        positions = [s.get() for s in self.sliders]
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=1)
        msg.points = [point]
        self.publisher.publish(msg)
        self.status_label.config(
            text=f"Sent: {[f'{p:.2f}' for p in positions]}",
            fg='#00ff88'
        )

    def reset_joints(self):
        for s in self.sliders:
            s.set(0.0)
        self.send_command()

    def on_close(self):
        self.root.destroy()
        rclpy.shutdown()
        sys.exit(0)

    def run(self):
        # ROS2 spin과 tkinter mainloop 병행
        def ros_spin():
            rclpy.spin_once(self, timeout_sec=0.01)
            self.root.after(10, ros_spin)
        self.root.after(10, ros_spin)
        self.root.mainloop()


def main():
    rclpy.init()
    gui = JointSliderGUI()
    gui.run()


if __name__ == '__main__':
    main()
