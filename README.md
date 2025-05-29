# magicdog_motion_sdk

## Summary
Motion SDK for multiple joint robot from MagicLab.

The magicdog_motion_sdk is used for secondary development with quadruped robot. It is a pure motion sdk and provids both low level and high level controllers. And it utilizes LCM to communicate with the controller board.

[简体中文](./README_ZH.md)

## Dependencies
* [LCM](https://github.com/lcm-proj/lcm)

Download lcm repo and build it with cmake.

```bash
git clone https://github.com/lcm-proj/lcm.git
cd lcm
mkdir build && cd build
cmake .. 
make
sudo make install
```

The dynamic library of lcm would be install in `/usr/local/lib`. If error that the lib is not found occurs when running the [examples](Run on the hardware), add the ld path in `~/.bashrc` file.
```bash
echo "export LD_LIBRARY_PATH=/usr/local/lib" >> ~/.bashrc
```

## Build and Install

Download SDK and build it.

```bash
git clone https://github.com/MagiclabRobotics/magicdog_motion_sdk.git
cd ${project}  # enter project (magiclab_mjr_sdk) directory
mkdir build && cd build
cmake ..
make

# install sdk
sudo ../scripts/install.sh
```

## Run with the remote PC

0. Start the robot and the control program on the controller board is self-started.

1. Build the connection between your PC (remote computer) and controller board with data cable.

    ![image](./doc/connection_port2.png)

    ![image](./doc/config_network.png)

2. Config the lcm network.
    On your PC,
    ```bash
    cd ${project}/scripts
    ./auto_lcminit.sh
    ```

3. Initialize the motion sdk running environment on the hardware,
    On your PC,
    
    ```bash
    cd ${project}/scripts
    ./sdk_init t
    ```

4. Ensure the robot is prepared for start, and then run the example (or your own remote controller),
    On your PC,
    
    ```bash
    cd ${project}/build
    ./high_level_walk
    ```
    
5. When the remote controller exits, the controller on the hardware still runs and robot state is set to `PureDamper`.