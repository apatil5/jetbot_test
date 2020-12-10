#!/usr/bin/env python
# license removed for brevity
import rospy
import math
import numpy as np
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray
import tf_conversions
from std_msgs.msg import Float32

class controller:
  
  xs   = 0
  ys   = 0
  yaw  = 0
  path =[]
    
  def odometrycallback(self, msg):

        controller.xs = msg.pose.pose.position.x
        controller.ys = msg.pose.pose.position.y	

	quaternion = (
    		msg.pose.pose.orientation.x,
    		msg.pose.pose.orientation.y,
    		msg.pose.pose.orientation.z,
    		msg.pose.pose.orientation.w)
	euler = tf_conversions.transformations.euler_from_quaternion(quaternion)
	#roll  = euler[0]
	#pitch = euler[1]
	controller.yaw = euler[2]
	#print (controller.yaw)
	
  def path_callback(self,ar_msg):
	i=0
        controller.path=[]

	for x in ar_msg.data : 
        	controller.path.append(x)
        #print(controller.path)


  def velocity(self):
        pub = rospy.Publisher("/jetbot_5/jetbot_base_controller/cmd_vel", Twist, queue_size=10)
        rospy.init_node('controller_kay')
        rate = rospy.Rate(100) # 10hz
        while not rospy.is_shutdown():
		xr       = controller.path[0]
		yr       = controller.path[1]
		theta_r  = controller.path[2]
       		refVel   = controller.path[3]
		refOmega = controller.path[4]
	
	        ky  = 10
	        kx  = 5*math.sqrt(refOmega*refOmega + ky*refVel*refVel)
	        kth = kx/abs(refVel);       

	        p_e1 = math.cos(controller.yaw)*(xr-controller.xs) + math.sin(controller.yaw)*(yr-controller.ys)
	        p_e2 = math.cos(controller.yaw)*(yr-controller.ys) - math.sin(controller.yaw)*(xr-controller.xs)
	        p_e3 = theta_r - controller.yaw

	        v1 = refVel*math.cos(p_e3) + kx*p_e1;
	        w1 = refOmega + refVel*(ky*p_e2 + kth*math.sin(p_e3))

	        v = min(max(0.18,abs(v1)),0.54)
	        w = min(max(-3.5,w1),3.5)  
		
		vel_msg=Twist()
		vel_msg.linear.x  = v
		vel_msg.angular.z = w

		print(v,w,[p_e1,p_e2,p_e3])	      	

       		#rospy.loginfo(vel_msg)
        	pub.publish(vel_msg)
        	
		rate.sleep()

if __name__ == '__main__': 
        
        try:         
	 ctr = controller()
	 rospy.Subscriber("/jetbot_5/base_link",Odometry,ctr.odometrycallback)
    	 rospy.Subscriber('/ref_array',Float64MultiArray,ctr.path_callback) 
         ctr.velocity()
          	
        except rospy.ROSInterruptException:
          pass
