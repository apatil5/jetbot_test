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
   
   double ang_error,r,distance,v,omega,xs,ys,yaw, path[];

   void odometrycallback(const nav_msgs::Odometry::ConstPtr msg) {
        
        xs = msg->pose.pose.position.x;
        ys = msg->pose.pose.position.y;

	tf::Quaternion q(
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

   void velocity(int r){
	n=r;
	ang_error = atan2(path[n-1]-ys, path[n-2]-xs)-yaw;      	
	distance =  sqrt( (path[n-1]-ys) * (path[n-1]-ys) + (path[n-2]-xs) * (path[n-2]-xs) );
   	
	if(abs(ang_error)<0.1 && distance>0.05){
	  v = 0.3;
	  omega = 0;
	}
   	else if ((ang_error > 3.14 ) || (ang_error > -3.14) ){
	   v = 0.0;
		omega = ang_error*0.2;
	}
	else {
	   v = 0.0;
	   omega= ang_error*0.2;}
   }   
};


int main(int argc, char **argv)
{
  ros::init(argc, argv, "Controller");
  ros::NodeHandle nh;

  Controller  ctr;
  ros::Subscriber sub_odom = nh.subscribe("/odom", 100, &Controller::odometrycallback, &ctr);
  ros::Subscriber sub_goal = nh.subscribe("/array", 100, &Controller::path_callback, &ctr);
 

  ros::Publisher vel_pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);
  ros::Rate loop_rate(1);
  
  ctr.velocity(0);
  geometry_msgs::Twist vel_msg;

  vel_msg.linear.x  = ctr.v;
  vel_msg.angular.z = ctr.omega; 
	
  int r=0;

  while(ros::ok()){
	ctr.velocity(r);
	geometry_msgs::Twist vel_msg;
	
	vel_msg.linear.x  = ctr.v;
	vel_msg.angular.z = ctr.omega;	
	
	vel_pub.publish(vel_msg);
 
	ROS_INFO("size: %d, dist:%f,ang_error: %f ", r,ctr.distance,ctr.ang_error) ;
	r++;
	ros::spinOnce();
  	loop_rate.sleep();
        	
  }
  return 0;
}
