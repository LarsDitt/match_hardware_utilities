# match Hardware Utilities

## Installation of DualShock Support

This package needs the mirMsgs package from `match_mobile_robotic`

### Setup workspace

Create catkin folder `system_ctl_ws` in the home dictionary

Clone `match_hardware_utilities` into the `src` folder

Clone submodule  `ds4ros` into the folder

Install Dualshock ds4drv driver to use ds4ros

    sudo -H pip install git+https://github.com/gerardcanal/ds4drv

Add ds4drv rule

    sudo wget https://raw.githubusercontent.com/chrippa/ds4drv/master/udev/50-ds4drv.rules -O /etc/udev/rules.d/50-ds4drv.rules

Update udevadm

    sudo udevadm control --reload-rules && sudo udevadm trigger

Build `system_ctl_ws` and reboot

### Connect the DualShock controller and configure autostart

Open bluetoothctl in a terminal

    bluetoothctl

Enable scan

    scan on

Press Share-button and PlayStation-button on DualShock controller for 5s

"Wireless Controller" with MAC-adress should pop up

Connect to Wireless Controller:

    connect "MAC"

Trust Wireless Controller

    trust "MAC"

Exit bluetoothctl

    exit

Configure the MAC adress in the `autostart.sh` file, reboot and test it using `bash autostart.sh`

### Install autostart.sh

Create systemd service

    nano /etc/systemd/system/autostart_ds4.service

Enter this configuration:

    [Unit]
    Description=ROS Autostart Service
    After=network.target  # Ensure the network is up before starting

    [Service]
    ExecStart=bash /home/rosmatch/system_ctl_ws/src/match_hardware_utilities/ds4_controller/scripts/autostart.sh
    StandardOutput=inherit
    StandardError=inherit
    Restart=always  # Automatically restart if the process crashes
    User=rosmatch
    Environment="ROS_MASTER_URI=http://mir:11311"

    [Install]
    WantedBy=multi-user.target

Reload and enable autostart

    sudo systemctl daemon-reload
    sudo systemctl enable autostart_ds4.service
