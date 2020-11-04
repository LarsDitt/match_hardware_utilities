#!/usr/bin/env python
import yaml
import collections
import os
import errno



import rospy
import rospkg
import actionlib
import numpy as np

from sensor_msgs.msg import JointState
from std_srvs.srv import Empty
from robot_teacher.srv import SetName,DriveTo
from trajectory_msgs.msg import JointTrajectory,JointTrajectoryPoint


class PoseFileHandler:
    def __init__(self):
        self.__filename=rospy.get_param("~file_name",str())  
        self.__joint_names=rospy.get_param("~joint_names",list())
        self.__save_srv=rospy.Service("~save_pose",SetName,self.__saveCallback__)                    
        self.__joint_states_dict=dict()
        self.__current_joint_sub=rospy.Subscriber("joint_states",JointState,self.__currentJointCallback__)
        self.__joint_states=dict()
        self.__load__()

    def __currentJointCallback__(self,msg):
            for index,name in enumerate(msg.name):
                if name in self.__joint_names:
                    self.__joint_states[name]=msg.position[index] 

    def __load__(self):
        if os.path.isfile(self.__filename):
            with open(self.__filename, 'r') as infile:
                raw=yaml.safe_load(infile)
                for pose in raw:
                    self.__joint_states_dict[pose]={joint_name:raw[pose][joint_name] for joint_name in self.__joint_names}
            print("Loaded yaml: ")
            print(yaml.safe_dump(self.__joint_states_dict,default_flow_style=False))
       

        
   
   
    def __saveCallback__(self,req):
        self.__joint_states_dict[req.name]=self.__joint_states
        self.__save__()


    def __save__(self):
        if self.__joint_states_dict:
            rospy.loginfo("Saving:")
            rospy.loginfo(self.__joint_states_dict)
            rospy.loginfo("to file "+self.__filename)

            if not os.path.exists(os.path.dirname(self.__filename)):
                try:
                    os.makedirs(os.path.dirname(self.__filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            with open(self.__filename, 'w') as outfile:
                yaml.safe_dump(self.__joint_states_dict,outfile,default_flow_style=False) 
    
    def getNames(self):
        return self.__joint_states_dict.keys()              
    
    def getStates(self,pose_name):
        return self.__joint_states_dict[pose_name]

    def __jointCallback__(self,msg):
        self.__joint_states=dict()
        for index,name in enumerate(msg.name):
            self.__joint_states[name]=msg.position[index]
    
    def __addStatesCallback__(self,req):
        rospy.loginfo("Adding joint state position: ")
        rospy.loginfo(self.__joint_states)
        rospy.loginfo("With name: ")
        rospy.loginfo(req.name)
        
        self.__joint_states_dict[req.name]={name:self.__joint_states[name] for name in self.__joint_names}  
        self.__save__()        
        return  len(self.__joint_states_dict)
  


   

class TeachedPoseHandler():
    def __init__(self):
        self.__file_handler=PoseFileHandler()

        self.__trajectory_commander=rospy.Publisher("position_joint_controller/command",JointTrajectory,queue_size=10)
       
        self.__current_joint_sub=rospy.Subscriber("joint_states",JointState,self.__currentJointCallback__)
       
        self.__drive_to_srv=rospy.Service("~drive_to",SetName,self.__driveTo__)
           
        self.__max_joint_velocity=rospy.get_param("~max_joint_velocity",0.08)        
        self.__joint_names=rospy.get_param("~joint_names",list())


        self.__joint_states=dict()

    def __currentJointCallback__(self,msg):
        for index,name in enumerate(msg.name):
            if name in self.__joint_names:
                self.__joint_states[name]=msg.position[index] 


    
    def __calcTime__(self,target_joints,current_joints):
        target=collections.OrderedDict(sorted(target_joints.items()))
        current=collections.OrderedDict(sorted(current_joints.items()))
        if target.keys()==current.keys():
            values=np.array(target.values(),dtype=np.float)-np.array(current.values(),dtype=np.float)
            values=np.abs(values)
            return rospy.Duration(np.max(values)/self.__max_joint_velocity)
        else:
            raise KeyError("Joints in target and current configuration do not fit")


    def __driveTo__(self,req):
        if req.name in self.__file_handler.getNames():     
            joint_states=self.__file_handler.getStates(req.name)
        else:
            raise KeyError("Pose name does not exist")

        if not self.__joint_states:
            raise ValueError("Current joint states are empty. Did you subscribe to correct topic?")     

        point=JointTrajectoryPoint()
        point.positions=joint_states.values()
        point.velocities=[0.0]*len(joint_states.values())
        point.accelerations=[0.0]*len(joint_states.values())
        point.effort=[0.0]*len(joint_states.values())
        point.time_from_start=self.__calcTime__(joint_states,self.__joint_states)       
       
        if point.time_from_start.to_sec()>0.1:
            joint=JointTrajectory()
            joint.joint_names=joint_states.keys()
            joint.points=[point]
            print(joint)
            self.__trajectory_commander.publish(joint)
            return 1
        return 0      
