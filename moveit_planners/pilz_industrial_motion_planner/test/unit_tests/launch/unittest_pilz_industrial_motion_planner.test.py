import launch_testing
import pytest
import unittest
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_testing.util import KeepAliveProc


@pytest.mark.rostest
def generate_test_description():

    # Load the context
    test_config = (
        MoveItConfigsBuilder("moveit_resources_prbt")
        .robot_description(
            file_path=get_package_share_directory("moveit_resources_prbt_support")
            + "/urdf/prbt.xacro"
        )
        .robot_description_semantic(file_path="config/prbt.srdf.xacro")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .cartesian_limits(file_path="config/cartesian_limits.yaml")
        .to_moveit_configs()
    )

    planning_plugin = {
        "planning_plugin": "pilz_industrial_motion_planner::CommandPlanner"
    }

    # run test
    unittest_pilz_industrial_motion_planner = Node(
        package="pilz_industrial_motion_planner",
        executable="unittest_pilz_industrial_motion_planner",
        name="unittest_pilz_industrial_motion_planner",
        parameters=[
            test_config.robot_description,
            test_config.robot_description_semantic,
            test_config.robot_description_kinematics,
            test_config.joint_limits,
            test_config.cartesian_limits,
            planning_plugin,
        ],
        output="screen",
    )
    return (
        LaunchDescription(
            [
                unittest_pilz_industrial_motion_planner,
                KeepAliveProc(),
                launch_testing.actions.ReadyToTest(),
            ]
        ),
        {
            "unittest_pilz_industrial_motion_planner": unittest_pilz_industrial_motion_planner
        },
    )


class TestTerminatingProcessStops(unittest.TestCase):
    def test_gtest_run_complete(
        self, proc_info, unittest_pilz_industrial_motion_planner
    ):
        proc_info.assertWaitForShutdown(
            process=unittest_pilz_industrial_motion_planner, timeout=4000.0
        )


@launch_testing.post_shutdown_test()
class TestOutcome(unittest.TestCase):
    def test_exit_codes(self, proc_info, unittest_pilz_industrial_motion_planner):
        launch_testing.asserts.assertExitCodes(
            proc_info, process=unittest_pilz_industrial_motion_planner
        )
