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

#include <iostream>
#include <unistd.h>
#include <math.h>
#include <cstring>

#include "common.h"
#include "DataCmdExchange.h"

int main() {
  DataCmdExchange io_interface;
  InputData data; 
  OutputData cmd; 

  memset(&data, 0., sizeof(data));
  memset(&cmd, 0., sizeof(cmd));

  double dt = 0.002;
  long cnt = 0;
  bool first_enter = true;
  bool first_step1 = true;
  bool first_step2 = true;
  bool first_step3 = true;
  bool first_step4 = true;

  while(1) {
    std::chrono::steady_clock::time_point t_start = io_interface.initDuration();

    // wait for connection
    if(!io_interface.isConnect()) {
      std::printf("Building connection ...\n");
      io_interface.waitDuration(t_start, dt);
      continue;
    }
    
    // receive data
    io_interface.receiveData(data);

    // ensure the initial state is Passive
    if (first_enter && data.robot_fsm_data!= 0) {
      cmd.robot_fsm_cmd = 0.;
      io_interface.sendCmd(cmd);
      io_interface.waitDuration(t_start, 1.);
      
      // check
      io_interface.receiveData(data);
      first_enter = (data.robot_fsm_data!= 0);
      
      if (first_enter)
        continue;
    }

    cnt++;
    if (cnt<4000) {
      if(first_step1) {
        first_step1 = false;
        std::printf("Enter into RecoveryStand FSM!\n");
      }

      cmd.robot_fsm_cmd = 2;
    }
    else if(cnt<9000) {
      if(first_step2) {
        first_step2 = false;
        std::printf("Enter into BalanceStand FSM!\n");
      }

      cmd.robot_fsm_cmd = 3;

      cmd.motion_cmd.body_height = 0.28;

      cmd.motion_cmd.rpy_des[0] = 0.2*sin(1.*(cnt-4000)*M_PI/5000.);
      cmd.motion_cmd.rpy_des[1] = 0.15*sin(2.*(cnt-4000)*M_PI/5000.);
      cmd.motion_cmd.rpy_des[2] = 0.2*sin(3.*(cnt-4000)*M_PI/5000.);
    }
    else if (cnt<19000) {
      if(first_step3) {
        first_step3 = false;
        std::printf("Enter into Trot FSM!\n");
      }

      cmd.robot_fsm_cmd = 4;

      cmd.motion_cmd.rpy_des[1] = 0.;
      cmd.motion_cmd.v_des[2] = 0.2;
      cmd.motion_cmd.step_height = 0.05;
    }
    else if(cnt<20000) {
      if(first_step4) {
        first_step4 = false;
        std::printf("Enter into BalanceStand FSM!\n");
      }

      cmd.robot_fsm_cmd = 3;
      cmd.motion_cmd.body_height = 0.3;
    }
    else 
      break;

    io_interface.sendCmd(cmd);
    io_interface.waitDuration(t_start, dt);
  }

  std::printf("The process is over!\nExisting...\n");
  return 0;
}