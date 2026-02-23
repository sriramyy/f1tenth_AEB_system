# This file is just used for a structure overview and does not actually
# implement any logic needed. 

# Imports here

class AEBNode(Node):
    def __init__(self):
        super().__init__('aeb_node')
        
        # Initialize any variables 

        # Subscribers and Publishers

    def odom_callback(self, msg):
        # Called whenever we get data from the odometry
        # Where msg is a LaserScan message
        pass

    def scan_callback(self, msg):
        # Called whenever we get data from the lidar scan
        # Where msg is an Odometry message 
        pass

    def emergency_brake(self):
        # Called when we need to stop so,
        # this should stop the car by publishing
        pass    

def main(args=None):
    rclpy.init(args=args)
    node = AEBNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()





