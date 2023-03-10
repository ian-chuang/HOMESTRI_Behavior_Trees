#! /usr/bin/env python3

import rospy
import actionlib
from move_groups import Arm, Gripper
from threading import Thread
from shr_interfaces.msg import ActionNodeAction
    
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class ManipulationActionServer():
    def __init__(self):
        super().__init__()

        self.arm = Arm('arm')
        self.gripper = Gripper('gripper')

        self.actserv = actionlib.SimpleActionServer(
            'manip_as', 
            ActionNodeAction, 
            execute_cb=self.action_cb, 
            auto_start=False
        )
        self.actserv.start()

    def action_cb(self, goal):
        id = goal.id

        if id == 'move arm to pose':
            self.start_thread_and_wait_for_result(self.arm.move_to_pose, (goal.pose, ))
        elif id == 'move arm to target':
            self.start_thread_and_wait_for_result(self.arm.move_to_target, (goal.target, ))
        elif id == 'move arm pregrasp approach':
            self.start_thread_and_wait_for_result(self.arm.pregrasp_approach, (goal.position, ))
        elif id == 'move arm cartesian path':
            self.start_thread_and_wait_for_result(self.arm.move_cartesian_path, (goal.pose, ))
        elif id == 'move gripper to target':
            self.start_thread_and_wait_for_result(self.gripper.move_to_target, (goal.target, ))
        elif id == 'move gripper to position':
            self.start_thread_and_wait_for_result(self.gripper.move_to_position, (goal.position, ))

    def start_thread_and_wait_for_result(self, function, args):
        thread = ThreadWithReturnValue(target=function, args=args)
        thread.start()

        while thread.is_alive():
            if self.actserv.is_preempt_requested():
                self.arm.stop()
                self.gripper.stop()
                self.actserv.set_preempted()
                thread.join()
                return
            rospy.sleep(0.02)
            
        success = thread.join()
        if not success:
            self.actserv.set_aborted()
            return

        self.actserv.set_succeeded()

if __name__ == "__main__":
    rospy.init_node('manipulation_action_server')
    manipulation_action_server = ManipulationActionServer()
    rospy.spin()