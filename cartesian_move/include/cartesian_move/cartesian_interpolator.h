#include <ros/ros.h>
#include <geometry_msgs/PoseStamped.h>
#include <actionlib/server/simple_action_server.h>
#include <cartesian_move/CartesianInterpolationAction.h>
#include <algorithm>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>


class CartesianInterpolator{
    public:
        CartesianInterpolator(ros::NodeHandle &nh);
    protected:
        virtual std::vector<geometry_msgs::PoseStamped> calcPath(geometry_msgs::PoseStamped source,geometry_msgs::PoseStamped target);
        virtual std::vector<geometry_msgs::PoseStamped> interpolate(tf2::Transform diff);
        tf2_ros::TransformListener listener_;
        tf2_ros::Buffer buffer_;
        ros::NodeHandle nh_;
        std::string base_frame_;
        std::string ee_frame_;
    private:
        double time_step_;
        double time_;
        double max_vel_;

        actionlib::SimpleActionServer<cartesian_move::CartesianInterpolationAction> as_;
        void executeCallback(const cartesian_move::CartesianInterpolationGoalConstPtr &goal);       
        std::vector<geometry_msgs::PoseStamped> path_;
     
     
        ros::Publisher pose_publisher_;
    
   
};
