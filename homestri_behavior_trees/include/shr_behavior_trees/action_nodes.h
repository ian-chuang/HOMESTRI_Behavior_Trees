#ifndef ACTION_NODE_H
#define ACTION_NODE_H

#include <ros/ros.h>

#include <shr_interfaces/ManipulationAction.h>
#include <shr_interfaces/ManipulationGoal.h>
#include <shr_interfaces/ManipulationResult.h>
#include <shr_interfaces/ManipulationFeedback.h>

#include "behaviortree_cpp_v3/behavior_tree.h"
#include <behaviortree_ros/bt_action_node.h>

#include <shr_behavior_trees/node_input_conversions.h>

using namespace BT;

class ManipulationAction: public RosActionNode<shr_interfaces::ManipulationAction>
{

public:
  ManipulationAction( ros::NodeHandle& handle, const std::string& name, const NodeConfiguration & conf):
RosActionNode<shr_interfaces::ManipulationAction>(handle, name, conf) {}

  static PortsList providedPorts()
  {
    return { 
      InputPort<std::string>("id"),
      InputPort<std::string>("description"),
      InputPort<geometry_msgs::Pose>("pose"),
      InputPort<std::string>("target"),
      InputPort<double>("position")
    };
  }

  bool sendGoal(GoalType& goal) override
  {
    if (!getInput<std::string>("id", goal.id)) {
      ROS_ERROR("missing required input [id]");
      return false;
    }
    if (!getInput<std::string>("description", goal.description)) {
      ROS_ERROR("missing required input [description]");
      return false;
    }
    getInput<geometry_msgs::Pose>("pose", goal.pose);
    getInput<std::string>("target", goal.target);
    getInput<double>("position", goal.position);
    return true;
  }

  NodeStatus onResult( const ResultType& res) override
  {
    return NodeStatus::SUCCESS;
  }

  virtual NodeStatus onFailedRequest(FailureCause failure) override
  {
    ROS_ERROR("ManipulationAction request failed %d", static_cast<int>(failure));
    return NodeStatus::FAILURE;
  }

  void halt() override
  {
    if( status() == NodeStatus::RUNNING )
    {
      ROS_WARN("ManipulationAction halted");
      BaseClass::halt();
    }
  }
};

#endif