# magicdog_sdk

## SDK Environment Requirements

This SDK requires the following software and hardware environment to function properly. Please ensure all dependencies are installed and configured before using the SDK.

### 1. Operating System

- Ubuntu 22.04 or later (recommended)  

#### System Configuration

1. The following configurations need to be added to the `/etc/security/limits.conf` file for regular users:

```
*    -   rtprio   98
```

2. To increase the per-socket receive buffer size, add the following configurations to `/etc/sysctl.conf` and apply them immediately with `sudo sysctl -p`:

```bash
net.core.rmem_max=20971520  
net.core.rmem_default=20971520  
net.core.wmem_max=20971520  
net.core.wmem_default=20971520  
```

### 2. Compiler & Toolchain

- GCC ≥ 11.4 (for Linux)
- CMake ≥ 3.16
- Make build system
- Eigen3

### 3. Programming Language

- C++20 (minimum)
- python3.10

## Build examples
To build the examples inside this reposity:
```
  mkdir build
  cd build
  cmake .. -DBUILD_EXAMPLES=ON
  make -j8
```

## C++ SDK Installation

To build your own application with this SDK, you can install the magicdog_sdk to specified directory:
```
  mkdir build
  cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=/opt/magic_robotics/magicdog_sdk
  make -j8
  sudo make install
```
You can refer to example/cmake_sample on how to import the `magicdog_sdk` into your CMake project.
```
  cd example/cmake_example
  mkdir build
  cd build
  cmake .. -DCMAKE_PREFIX_PATH=/opt/magic_robotics/magicdog_sdk
  make -j8
```
Note that the path specified by -DCMAKE_PREFIX_PATH must be the same as the installation directory used above.

### Python SDK Installation

The Python bindings are automatically installed when you build the SDK. After building, you can use the Python SDK by setting the appropriate environment variables:

```bash
# Set up environment variables for Python SDK
export PYTHONPATH=/opt/magic_robotics/magicdog_sdk/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/opt/magic_robotics/magicdog_sdk/lib:$LD_LIBRARY_PATH
```

You can also add these environment variables to your shell profile (e.g., `~/.bashrc`) for permanent setup.

## Notice

- The Python SDK provides the same functionality as the C++ SDK with a more Pythonic interface
- All Python examples are located in the `example/python/` directory
- Make sure to set the correct environment variables (`PYTHONPATH` and `LD_LIBRARY_PATH`) when using the Python SDK
- The Python bindings are automatically generated during the build process

> For more reference documentation, please go to [MagicLab Document Center](https://support.magiclab.top/)

> For more reference information, please go to [MagicRobotics](https://github.com/MagiclabRobotics)
