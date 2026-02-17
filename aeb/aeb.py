import rclpy
from rclpy.node import Node
import numpy as np
# Import standard ROS2 message types used in F1TENTH
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from ackermann_msgs.msg import AckermannDriveStamped

class AEBNode(Node):
    # --- INITIALIZATION -- this is where we declare our publishers & subscribers and variables
    def __init__(self):
        super().__init__('aeb_node')
        
        # init variables
        self.speed = 0.0
        self.ttc_threshold = 0.4 # Threshold in seconds

        # --- SUBSCRIBERS AND PUBLISHERS ---
        # note that if the topic names are different then we change them here
        # subscribers: Listen to Lidar and Odom
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # publisher: Send stop command to the car
        self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)

    # --- ODOM CALLBACK --- this is called whenever we get data from the odom, so we want to update our speed var with the car speed from odom
    def odom_callback(self, msg):
        # get current speed from odom
        self.speed = msg.twist.twist.linear.x

    
    # --- SCAN CALLBACK --- this is called whenever we get data from the LIDAR, so we want to check the forward LIDAR beam for the distance
    def scan_callback(self, msg):
            # convert to numpy array for efficiency
            ranges = np.array(msg.ranges)
            
            # define our center 20 degrees
            # with 0.25 deg resolution, 20 degrees = 80 beams total (40 each side)
            center_idx = len(ranges) // 2
            window = 40 
            
            # slice the arrays to only look at the front
            front_ranges = ranges[center_idx - window : center_idx + window]
            
            # calc angles only for this specific slice
            # calculate the specific angles to maintain TTC accuracy
            angle_min_front = msg.angle_min + (center_idx - window) * msg.angle_increment
            angle_max_front = msg.angle_min + (center_idx + window) * msg.angle_increment
            front_angles = np.linspace(angle_min_front, angle_max_front, len(front_ranges))

            # calc TTC only for the front slice
            # notice we use the self.speed variable here which is from our odom callback
            range_rate = self.speed * np.cos(front_angles)
            ttc = front_ranges / np.maximum(range_rate, 1e-6)

            # check the minimum TTC in our restricted view
            # also lets print the ttc for debugging purposes
            min_ttc = np.min(ttc)

            # Use ROS2 logging with a 0.5-second throttle so it doesn't spam the screen
            self.get_logger().info(f"Current TTC: {min_ttc:.2f} seconds", throttle_duration_sec=0.5)

            if min_ttc < self.ttc_threshold:
                self.emergency_brake()

    # --- EMERGENCY BRAKE --- this is called when we actually need to activate the emergency brake system
    def emergency_brake(self):
        # create the stop message
        stop_msg = AckermannDriveStamped()
        stop_msg.drive.speed = 0.0

        # publish the stop message
        self.drive_pub.publish(stop_msg)
        self.get_logger().warn("[AEB TRIGGERED] BRAKING!")

def main(args=None):
    rclpy.init(args=args)
    node = AEBNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()