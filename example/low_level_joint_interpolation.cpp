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

  float j1[] = { 0.0000, 1.0477, -2.0944};   // base height 0.2 
  float j2[] = { 0.0000, 0.7231, -1.4455};   // base height 0.3
  float inital_q[12] = {0.};

  double dt = 0.002;
  long cnt = 0;
  bool first_enter = true;
  bool first_step1 = true;

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
    cmd.robot_fsm_cmd = 5;

    if (cnt==1) {
      memcpy(inital_q, data.motor_data.q, sizeof(inital_q));
    }

    if(cnt<1000) {
      double t = 1.0*cnt/1000.;
      t = std::min(std::max(t, 0.), 1.);

      for (int i=0; i<12; i++)
        cmd.motor_cmd.q_des[i] = (1-t)*inital_q[i] + t*j1[i%3];
    }
    else if(cnt<1750) {
      if(first_step1) {
        first_step1 = false;
        std::printf("Body UP and DOWN cycle!\n");
        std::printf("[Ctrl C] to exit...\n");
      }

      double t = 1.0*(cnt-1000)/700.;
      t = std::min(std::max(t, 0.), 1.);

      for (int i=0; i<12; i++)
        cmd.motor_cmd.q_des[i] = (1-t)*j1[i%3] + t*j2[i%3];
    }
    else if(cnt<2500) {
      double t = 1.0*(cnt-1750)/700.;
      t = std::min(std::max(t, 0.), 1.);

      for (int i=0; i<12; i++)
        cmd.motor_cmd.q_des[i] = (1-t)*j2[i%3] + t*j1[i%3];
    }
    else {
      cnt = 1000;
    }

    for (int i=0; i<12; i++) {
      cmd.motor_cmd.kp[i] = 100.;
      cmd.motor_cmd.kd[i] = 1.2;
    }

    io_interface.sendCmd(cmd);
    io_interface.waitDuration(t_start, dt);
  }

  return 0;
}