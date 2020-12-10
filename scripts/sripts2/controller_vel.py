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
from control.matlab import lqr

class controller:
  
  xs   = 0
  ys   = 0
  vs   = 0
  yaw  = 0
  ws =0
  path =[]
    
  def odometrycallback(self, msg):

        controller.xs = msg.pose.pose.position.x
        controller.ys = msg.pose.pose.position.y	
	controller.vs = msg.twist.twist.linear.y
	controller.ws = msg.twist.twist.angular.z
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
	
	#controller gains
	alpha_v = 0.4;
	alpha_w = 0.4;
	lambda_v = 0.2;
	lambda_w = 0.2;

	kv1 = 0.1
	kv0 = 0.05
	kw1 = 0.01
	kw0 = 1
	pi  = np.pi
	dt = 0.012

        while not rospy.is_shutdown():
		#xr       = controller.path[0]
		#yr       = controller.path[1]
		#theta_r  = controller.path[2]
       		#refVel   = controller.path[3]
		#refOmega = controller.path[4]

		
		curPose = [controller.xs,controller.ys,np.mod(controller.yaw,6.28),controller.vs,controller.ws]
		refPose = controller.path[:3]		
		refVel  = np.matrix(controller.path[-2:])
		     
		t = (np.matrix([refPose]) - np.matrix([curPose[:3]]))
		t = np.transpose(t)
		x=t[2,0]
		
		if (-3.14>x>=-6.28):
			x= x+6.28
			t[2,0]=x
		elif 3.14<x<=6.28:
			x=x-6.28
			t[2,0]=x	
		

		p_e = np.matrix( [[ math.cos(curPose[2]), math.sin(curPose[2]), 0 ],
				  [-math.sin(curPose[2]), math.cos(curPose[2]), 0],
				  [0 ,0 ,1]])*t
		
			    
		# kayacan tracking controller
		A = np.matrix(
			     [ [0,            curPose[4],          0],
			       [-curPose[4],   0,        refVel[0,0]],
			       [ 0,            0,                  0] ])

		B = np.matrix([[1, 0],
			       [0, 0],
			       [0, 1]])
		   
		Q =np.diag([1000,1000,5]);#[1000,1000,0.0005]
		R= np.diag([100,1]);#100,0.1
		   
		K =lqr(A,B,Q,R);
			  
		u_b = K[0]*p_e;                

		#Forward learning rate controller  
		
		e1_dot  =  curPose[4]*p_e[1]-curPose[3]+ refVel[0,0]
		e2_dot  = -curPose[4]*p_e[0] + refVel[0,0]*p_e[2]
		e2_dot2 = -p_e[1]*refVel[0,1]**2 + refVel[0,1]*curPose[3] - refVel[0,0]*curPose[4]

		kv1_dot = alpha_v*refVel[0,0]*(e1_dot + lambda_v * p_e[0]);
		kv0_dot = alpha_v*(e1_dot + lambda_v * p_e[0]);
		kw1_dot = alpha_w*refVel[0,0]*refVel[0,1]*(e2_dot2+2*lambda_w*e2_dot+lambda_w**2*p_e[1]);
		kw0_dot = alpha_w*refVel[0,0]*(e2_dot2+2*lambda_w*e2_dot+ lambda_w**2*p_e[1]);

		kv1 = kv1 + kv1_dot*dt;
		kv0 = kv0 + kv0_dot*dt;
		kw1 = kw1 + kw1_dot*dt;
		kw0 = kw0 + kw0_dot*dt;

		vf = refVel[0,0]*kv1 + kv0;
		wf = refVel[0,1]*kw1 + kw0;

		v =  u_b[0,0] + vf
		w =  u_b[1,0] + wf
              
	        v = min(0.3,abs(v))
	        w = min(max(-3.5,w),3.5)  
		
		vel_msg=Twist()
		vel_msg.linear.x  = v
		vel_msg.angular.z = w

		print(t[2,0],p_e[2,0])	      	

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
