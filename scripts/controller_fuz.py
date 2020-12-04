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
import skfuzzy as fuz
from skfuzzy import control as ctrl
from fuz_fun import *

class controller:
  
  xs   = 0
  ys   = 0
  vs   = 0
  yaw  = 0
  path =[]
    
  def odometrycallback(self, msg):

        controller.xs = msg.pose.pose.position.x
        controller.ys = msg.pose.pose.position.y	
	controller.vs = msg.twist.twist.linear.y
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
        pub = rospy.Publisher('/cmd_vel', Twist, queue_size=100)
        rospy.init_node('controller_kay')
        rate = rospy.Rate(100) # 10hz
	pi  = np.pi
	dt = 0.012

        while not rospy.is_shutdown():
		#xr       = controller.path[0]
		#yr       = controller.path[1]
		#theta_r  = controller.path[2]
       		#refVel   = controller.path[3]
		#refOmega = controller.path[4]
		
		refPose = controller.path[:3]
		curPose = [controller.xs,controller.ys,controller.yaw]
		refVel  = np.matrix(controller.path[-2:])

		t = (np.matrix([refPose]) - np.matrix([curPose[:3]]))
		t=np.transpose(t)
		x=t[2,0]
		
		if (-3.14>x>=-6.28):
			x= x+6.28
			t[2,0]=x
		elif 3.14<x<=6.28:
			x=x-6.28
			t[2,0]=x	
	
	        #Error
		d_e= math.sqrt((refPose[0] - curPose[0])**2 + (refPose[1] - curPose[1])**2)
		theta_e = t[2,0]

		p_e = [d_e, theta_e]

		theta_l = math.atan2((refPose[1] - curPose[1]),(refPose[0] - curPose[0])) - curPose[2]

		if (theta_l>=-pi and theta_l<=pi):
		    theta = theta_l
		elif (theta_l>=-2*pi and theta_l<-pi):
		    theta = theta_l + 2*pi
		elif (theta_l>pi and theta_l<=2*pi):
		    theta = 2*pi - theta_l
		else :
		    theta = theta_l
		    
		dis_e = d_e + dt*(refVel[0,0]*math.cos(refPose[2]) - controller.vs * math.cos(theta))

		
		if (abs(dis_e)< 2*refVel[0,0]*dt):
		    th_e_scale = p_e[1] / 6.28
		else:
		    th_e_scale = theta/6.28
		    
		cmnd = fuz_fun(dis_e, th_e_scale)		

	        v = min(0.25,abs(cmnd[0]))
	        w = min(max(-3.5,cmnd[1]),3.5)  
		
		vel_msg=Twist()
		vel_msg.linear.x  = v
		vel_msg.angular.z = w

		print(w,th_e_scale)	      	

       		#rospy.loginfo(vel_msg)
        	pub.publish(vel_msg)
        	
		rate.sleep()

if __name__ == '__main__': 
        
        try:         
	 ctr = controller()
	 rospy.Subscriber('/odom',Odometry,ctr.odometrycallback)
    	 rospy.Subscriber('/ref_array',Float64MultiArray,ctr.path_callback) 
         ctr.velocity()
          	
        except rospy.ROSInterruptException:
          pass





    
