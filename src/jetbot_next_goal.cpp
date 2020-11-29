#include <ros/ros.h>
#include <geometry_msgs/Pose2D.h>
#include <nav_msgs/Odometry.h>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <chrono>
#include <random>
#include <math.h>
using namespace std;

class distanceMonitor {
  public:
   double xs,ys,xg,yg,distance;
   void Crnt_state_callback(const nav_msgs::Odometry::ConstPtr& msg){
     xs = msg->pose.pose.position.x;
     ys = msg->pose.pose.position.y;
   }
   void Crnt_goal_callback(const geometry_msgs::Pose2D::ConstPtr& msg){
     xg = msg->x;
     yg = msg->y;
   }

   void cal_dist(){
     distance = sqrt((xs-xg)*(xs-xg) + (ys-yg)*(ys-yg));
    }
   bool eval()
   {
     if (distance<0.1){
	     return true;
     }
     else {return false;}
   }

};

double randnum (double a, double b)
{
  unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
  static std::default_random_engine generator (seed);
  std::uniform_real_distribution<double> distribution (a,b);
  return distribution(generator);
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "jetbot_next_goal");
  ros::NodeHandle nh;
  ros::Rate loop_rate(83);
  distanceMonitor dm;

  ros::Subscriber sub_state = nh.subscribe("/odom", 100, &distanceMonitor::Crnt_state_callback, &dm);
  ros::Subscriber sub_goal  = nh.subscribe("/goal", 100, &distanceMonitor::Crnt_goal_callback, &dm);

  dm.cal_dist();
  bool goal_reached = dm.eval(); 

  ros::Publisher goal_pub = nh.advertise<geometry_msgs::Pose2D>("/goal", 100);
 
  double temp_x=0,temp_y=0;
  
  if(goal_reached){  
	 
	  temp_x = randnum(-2.3,2.3);
	  temp_y = randnum(-2.3,2.3);
  }
  else{
  
  	  temp_x = dm.xg;
          temp_y = dm.yg;
  }
  
  while(ros::ok()){

  	dm.cal_dist();
	bool goal_reached = dm.eval();
	  
	geometry_msgs::Pose2D msg;

	  if(goal_reached){
          	temp_x = randnum(-2.3,2.3);
          	temp_y = randnum(-2.3,2.3);
  	   }
  	  else{
          temp_x = dm.xg;
          temp_y = dm.yg;
   	}
	
       	msg.x = temp_x;
	msg.y = temp_y;
  
  	goal_pub.publish(msg);
  	//ROS_INFO("goal dist : %f",dm.distance);
  
 	ros::spinOnce();
 	loop_rate.sleep();
     } 
  return 0;
}
