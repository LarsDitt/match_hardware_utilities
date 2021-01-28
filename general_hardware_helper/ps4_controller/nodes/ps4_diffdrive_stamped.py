#!/usr/bin/env python
import rospy
from ps4_controller.PlayStationDiffDrive import PlayStationDiffDrive
from geometry_msgs.msg import TwistStamped

if __name__=="__main__":
    rospy.init_node("ps4_diffdrive_controller")
    ps4=PlayStationDiffDrive(TwistStamped)
    ps4.run()
    rospy.spin()