#!/bin/bash

# Variables
TARGET_DEVICE_NAME="Wireless Controller"
TARGET_DEVICE_ADDRESS="48:18:8D:4F:77:13"  # Replace with your device MAC address
CATKIN_WS="/home/rosmatch/system_ctl_ws"  # Path to your specific Catkin workspace
LAUNCH_FILE="ps4_controller_startup.launch"  # Launch file to be executed
PACKAGE_NAME="ds4_controller"  # ROS package containing the launch file

# Function to check if Bluetooth device is available
function find_bluetooth_device() {
    # Check if the target device is in the list of paired devices
    hcitool con | grep -i "$TARGET_DEVICE_ADDRESS"
    if [ $? -eq 0 ]; then
        echo "Found target device: $TARGET_DEVICE_NAME at $TARGET_DEVICE_ADDRESS"
        return 0
    else
        return 1
    fi
}

# Function to start the ROS launch file
function start_ros_launch() {
    # Source the setup.bash for the specific Catkin workspace
    source "$CATKIN_WS/devel/setup.bash"
    
    # Start the ROS launch file
    echo "Starting ROS launch file..."
    roslaunch "$PACKAGE_NAME" "$LAUNCH_FILE"
}

# Main loop to wait for the Bluetooth device to connect
while true; do
    echo "Waiting for Bluetooth device $TARGET_DEVICE_NAME ($TARGET_DEVICE_ADDRESS)..."
    
    # Check if the Bluetooth device is found
    if find_bluetooth_device; then
        # If found, start the ROS launch file
        start_ros_launch
        break
    else
        echo "$TARGET_DEVICE_NAME not found. Retrying in 5 seconds..."
        sleep 5  # Wait before retrying
    fi
done
