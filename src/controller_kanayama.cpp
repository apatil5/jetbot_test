#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <nav_msgs/Odometry.h>
#include <std_msgs/Float64MultiArray.h>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <math.h>
#include <vector>
using namespace std;
#include <tf/tf.h>
#include <geometry_msgs/Pose2D.h>
#include <algorithm>
#include <iterator>

class Controller {
  public:    
   int n=20,s=20,i=0;

   vector<double> vec;
   
   double p_e1=0,p_e2=0,p_e3=0,ang_error,r,distance,v,w,xs,ys,yaw, path[];

   void odometrycallback(const nav_msgs::Odometry::ConstPtr msg) {
        
        xs = msg->pose.pose.position.x;
        ys = msg->pose.pose.position.y;

	tf::Quaternion q(-+
	msg->pose.pose.orientation.x,
	msg->pose.pose.orientation.y,
	msg->pose.pose.orientation.z,
	msg->pose.pose.orientation.w);
	tf::Matrix3x3 m(q);
	double roll,pitch;
	m.getRPY(roll, pitch, yaw);	
   }
   
   void path_callback(const std_msgs::Float64MultiArray::ConstPtr& msg){
     	i=0;
	vec.clear();
	for(vector<double>::const_iterator it = msg->data.begin(); it != msg->data.end(); ++it)
	{
		path[i] =*it;
	
		vec.push_back(*it);	
		i++;
	}
	s = i;
		
   }

   void velocity(){
	n=i;

	double refVel = path[3], refOmega=path[4];

	double ky  = 200;
	double kx  = 0.01*sqrt(refOmega*refOmega + ky*refVel*refVel);
	double kth = 0.05*kx/abs(refVel);

	double xr= path[0], yr= path[1], theta_r = path[2];
	
	p_e1 = cos(yaw)*(xr-xs) + sin(yaw)*(yr-ys);
        p_e2 = cos(yaw)*(yr-ys) - sin(yaw)*(xr-xs);
	p_e3 = theta_r - yaw;	
       
        v = refVel*cos(p_e3) + kx*p_e1;
        w = refOmega + refVel*(ky*p_e2 + kth*sin(p_e3));

	v = min(0.25,abs(v));
	w = min(max(-3.5,w),3.5);

   }   
};


int main(int argc, char **argv)
{
  ros::init(argc, argv, "Controller");
  ros::NodeHandle nh;

  Controller  ctr;
  ros::Subscriber sub_odom = nh.subscribe("/odom", 100, &Controller::odometrycallback, &ctr);
  ros::Subscriber sub_goal = nh.subscribe("/ref_array", 100, &Controller::path_callback, &ctr);
 

  ros::Publisher vel_pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 83);
  ros::Rate loop_rate(83);
  
  ctr.velocity();
  geometry_msgs::Twist vel_msg;

  vel_msg.linear.x  = ctr.v;
  vel_msg.angular.z = ctr.w; 
	
  double r1;

  while(ros::ok()){
	ctr.velocity();
	geometry_msgs::Twist vel_msg;
	
	vel_msg.linear.x  = ctr.v;
	vel_msg.angular.z = ctr.w;	
	
	vel_pub.publish(vel_msg);
 
        ROS_INFO("vel :%f, omega: %f pe1: %f pe2: %f pe3: %f", ctr.v,ctr.w, ctr.p_e1,ctr.p_e2,ctr.p_e3) ;
	
	ros::spinOnce();
  	loop_rate.sleep();
        	
  }
  return 0;
}
