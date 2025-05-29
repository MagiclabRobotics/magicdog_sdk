/******************************************************************************
Copyright (c) 2025, Magiclab Robotics

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
******************************************************************************/

#ifndef _MAGICLAB_QUAD_SDK_COMMON_
#define _MAGICLAB_QUAD_SDK_COMMON_

/**
 * @brief IMU raw data.
 */
struct ImuData
{
  float quat[4];    // raw quaternion, ordered by w, x, y, z
  float gry[3];     // raw angular velocity, ordered by x, y, z [rad/s]
  float acc[3];     // raw linear acceleration, ordered by x, y, z [m/s^2]
};

/**
 * @brief 12 joints data.
 * The leg order is FR (front-right), FL (front-left), RR (rear-right) and RL (rear-left).
 * Joint order for each leg is HAA, HFE and KFE. 
 */
struct MotorData
{
  float q[12];    
  float dq[12];
  float tau_est[12];
};

/**
 * @brief Estimated data. 
 * The start pose is set to p(0., 0., 0.) and rpy(0., 0., 0.).
 * This estimated results cannot be used in LowLevelControl Mode due to the loss of contact schedule.
 */
struct EstimateData
{
  int64_t timestamp;   // tiem stamp of structed data on the hardware
  
  float p[3];          // base position, ordered by x, y, z
  float v_body[3];     // base velocity in body frame, ordered by x, y, z
  float v_world[3];    // base velocity in world frame, ordered by x, y, z

  float rpy[3];       // eular angles, roll, pitch, yaw
  float quat[4];      // quaternion, ordered by x, y, z, w
  float w_body[3];    // base angilar velocity in body frame, ordered by x, y, z
  float w_world[3];   // base angilar velocity in world frame, ordered by x, y, z

  float contact[4];   // contact state, only assigned in Trot robot state
};

/**
 * @brief 12 joints motor cmd.
 * The leg order is FR (front-right), FL (front-left), RR (rear-right) and RL (rear-left).
 * Joint order for each leg is HAA, HFE and KFE. 
 * Here the order of 12 joints are FR-HAA, FR-HFE, FR-KFE, FL-*, RR-*, RL-*.
 * 
 * The final desired torque command, which is send to the motor, is calculated in
 *      tau_final = tau_des + kp*(q_des - q_cur) + kd*(dq_des - dq_cur).
 */
struct MotorCmd 
{
  float q_des[12];     // desired joint position
  float dq_des[12];    // desired joint velocity
  float tau_des[12];   // desired feed-forward torque

  float kp[12];        // P gain, must be positive
  float kd[12];        // D gain, must be positive
};

/**
 * @brief Commands for integrated motions.
 */
struct MotionCmd 
{
  /**
   * @brief Desired orientation represented by eular angles, ordered by roll (x), pitch (y), 
   * and yaw (z).
   * 
   * In fsm BalanceStand (3) state:
   *    roll     -0.52 ~ +0.52   [rad]
   *    pitch    -0.25 ~ +0.30   [rad]
   *    yaw      -0.65 ~ +0.65   [rad]
   */
  float rpy_des[3];

  /**
   * @brief Desired velocities, ordered by linear x (vx [m/s]), linera y (vy [m/s]) and
   * angular z (wz [rad/s]).
   * 
   * In fsm Trot (4) state:
   *    vx   -1.2 ~ 1.2   [m/s] 
   *    vy   -0.5 ~ 0.5   [m/s] 
   *    wz   -2.5 ~ 2.5   [m/s] 
   */
  float v_des[3];

  /**
   * @brief Desired body height [m].
   * 
   * In fsm BalanceStand (3) state:
   *    body_height  0.15 ~ 0.35 [m]
   */
  float body_height;

  /**
   * @brief Desired foot step hieght for swing leg in locomotion.
   * 
   * In fsm Trot (4) state:
   *    step_height  0.01 ~ 0.15 [m]
   */
  float step_height;
};

/**
 * @brief IO structure
 */
struct InputData 
{
  int8_t robot_fsm_data;

  ImuData imu_data;
  MotorData motor_data;
  EstimateData estimate_data;
};

struct OutputData 
{ 
  /**
   * @brief Set robot state in fsm.
   * 
   * Support:
   *    0: Passive      
   *    1: PureDamper
   *    2: RecoveryStand
   *    3: BalanceStand
   *    4: Trot
   *    5: LowLevelControl
   * 
   * Allowed Transition:
   *    0 -> 2, 5
   *    1 -> 0
   *    2 -> 0, 1, 3, 4, 5
   *    3 -> 0, 1, 2, 4
   *    4 -> 0, 1, 3
   *    5 -> 0, 1, 2
   */
  int8_t robot_fsm_cmd;

  MotorCmd motor_cmd;
  MotionCmd motion_cmd;
};


#endif /* _MAGICLAB_QUAD_SDK_COMMON_ */
