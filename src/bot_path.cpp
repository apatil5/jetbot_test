#include <ros/ros.h>
#include <geometry_msgs/Pose2D.h>
#include <nav_msgs/Odometry.h>
#include <std_msgs/Float64MultiArray.h>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <math.h>
#include <vector>


using namespace std;

class Path_maker {
  public:
   double xg,yg;
  
   double xs,ys;    
   
   void Crnt_state_callback(const nav_msgs::Odometry::ConstPtr& msg){
     xs = 0;//msg->pose.pose.position.x;
     ys = 0;//msg->pose.pose.position.y;
   }
   
   void Crnt_goal_callback(const geometry_msgs::Pose2D::ConstPtr& msg){
     xg = 2.3;//msg->x;
     yg = 0;//msg->y;
   }
/*dynamic path
   void gen_path(int n){
     double path[n][2];
     double dx=(xg-xs)/n , dy =(yg-ys)/n;
     for (int i = 0; i < n; i++){
        vector<double> temp(2);
        path[i][0]=(xs+(i+1)*dx);
        path[i][1]=(ys+(i+1)*dy);
     }
    }*/

//static

  void gen_path(int n){
     double path[n][2];
     double dx=(xg-xs)/n , dy =(yg-ys)/n;
     for (int i = 0; i < n; i++){
        vector<double> temp(2);
        path[i][0]=(xs+(i+1)*dx);
        path[i][1]=(ys+(i+1)*dy);
     }
  }
  
};


int main(int argc, char **argv)
{
  ros::init(argc, argv, "bot_path");
  ros::NodeHandle nh;
  
  Path_maker pm;

  ros::Subscriber sub_state = nh.subscribe("/odom", 100, &Path_maker::Crnt_state_callback, &pm);
  ros::Subscriber sub_goal  = nh.subscribe("/goal", 100, &Path_maker::Crnt_goal_callback, &pm);
  int n1=100;
  pm.gen_path(n1);
  
  ros::Publisher path_pub = nh.advertise<std_msgs::Float64MultiArray>("/array", 100);
  ros::Rate loop_rate(10);

  vector<vector<double>> temp;	

  while(ros::ok()){
        
	std_msgs::Float64MultiArray ary_msg; 
  	ary_msg.data.clear();
	for (int x=0 ; x < n1; x++)
	{
  		ary_msg.data.push_back(pm.xs+(pm.xg-pm.xs)*x/n1);
		ary_msg.data.push_back(pm.ys+(pm.yg-pm.ys)*x/n1);
	}
	
	path_pub.publish(ary_msg);
/*	ROS_INFO("I published something! %f,%f",ary_msg.data[18],ary_msg.data[19]);
*/ 	
	ros::spinOnce();
  	loop_rate.sleep();
  }
  return 0;
}
