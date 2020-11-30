#include <ros/ros.h>
#include <math.h>
#include <geometry_msgs/Pose2D.h>
#include <nav_msgs/Odometry.h>
#include <std_msgs/Float64MultiArray.h>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <cmath>
#include <vector>


using namespace std;

int main(int argc, char **argv)
{
  ros::init(argc, argv, "ref_path");
  ros::NodeHandle nh;
  
  ros::Publisher path_pub = nh.advertise<std_msgs::Float64MultiArray>("/ref_array", 100);
  
  int LR= 1;
  ros::Rate loop_rate(83);

  double dt = 0.012;
  double theta=0;
  
  double v_ref = 0.25,omega_ref= 0.1;  
  
  double x=0,y=0,count=0;

  while(ros::ok()){
        
	std_msgs::Float64MultiArray ary_msg; 
  	ary_msg.data.clear();
	
  	/*//st line
	 * ary_msg.data.push_back(x);//r*cos(theta));
	ary_msg.data.push_back(0);//r*sin(theta));
	ary_msg.data.push_back(0);//fmod((theta+1.57), 6.28));
	ary_msg.data.push_back(v_ref);
	ary_msg.data.push_back(0);
	//theta = theta + omega_ref*dt;
	x = x + 0.0030;*/
	
	//circle
/*	ary_msg.data.push_back(x);
        ary_msg.data.push_back(y);
        ary_msg.data.push_back(theta);
        ary_msg.data.push_back(v_ref);
        ary_msg.data.push_back(omega_ref);
	
	x= x+v_ref*dt*cos(theta);
	y= y+v_ref*dt*sin(theta);
	theta = theta + omega_ref*dt;
*/
	//square
        ary_msg.data.push_back(x);
        ary_msg.data.push_back(y);
        ary_msg.data.push_back(theta);
        ary_msg.data.push_back(v_ref);
        ary_msg.data.push_back(0);
	
	int cs = floor(count/500);
	cs = (cs%4);
	double l = 0.003;
	switch(cs){
	  case 0 :
        	x= x+l;
        	y= 0;
        	theta =0;
		break;
	  case 1 :
                y= y+l;
                theta = 1.57;
		break;
          case 2 :
                x= x-l;
                theta = 3.14;
		break;
          case 3 :
                x=0;
                y= y-l;
                theta =4.71;
		break;
	}  
	
	count++;

	path_pub.publish(ary_msg);
	//ROS_INFO("x_ref: %f, y_ref:%f, theta_ref: %f, sin : %f cos : %f",ary_msg.data[0],ary_msg.data[1],ary_msg.data[2],sin(ary_msg.data[2]),cos(ary_msg.data[2]));
 	
	ros::spinOnce();
  	loop_rate.sleep();
  }
  return 0;
}
