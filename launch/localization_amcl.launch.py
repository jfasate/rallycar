import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('rallycar')

    # 1. Start hardware
    hardware_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("rallycar"),
                "launch",
                "rallycar_hardware.launch.py",
            )
        )
    )

    # 2. Load the map
    map_server_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("rallycar"),
                "launch",
                "examples",
                "load_map.launch.py",
            )
        ),
        launch_arguments={
            "map_file": os.path.join(
                get_package_share_directory("rallycar"),
                "resources",
                "maps",
                "1268v2.yaml",
            ),
        }.items(),
    )

    # 3. Start scan matching for odometry
    scanmatching_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("rallycar"),
                "launch",
                "include",
                "scanmatching_slam.launch.py"
            )
        )
    )

    # 4. Start AMCL
    amcl_node = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl_node",
        output="screen",
        parameters=[
            os.path.join(
                get_package_share_directory("rallycar"), "param", "amcl.param.yaml"
            ),
            {"tf_broadcast": True},
        ],
    )

    # 5. Lifecycle manager for Nav2 nodes
    nav2_activation_node = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="nav2_starter",
        output="screen",
        parameters=[{"autostart": True, "node_names": ["map_server", "amcl_node"]}],
    )

    # 6. RViz for visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(pkg_share, 'resources/rviz_configs/localization.rviz')]
    )

    return LaunchDescription([
        hardware_launch,
        map_server_launch,
        scanmatching_launch,
        #amcl_node,
        #nav2_activation_node,
        #rviz_node,
    ])
