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

#ifndef _MAGICLAB_QUAD_SDK_DATA_CMD_EXCHANGE_
#define _MAGICLAB_QUAD_SDK_DATA_CMD_EXCHANGE_

#include <memory>
#include <thread>
#include <chrono>
#include <time.h>

#include "common.h"

/**
 * @brief Receive data using LCM.
 */
class LcmReceiver;

/**
 * @brief Input output interface. It receives raw and estimated data and sends 
 * control commands. It provides duration setting in while loop as well.
 */
class DataCmdExchange {
public:
  using time_point = std::chrono::steady_clock::time_point;

  DataCmdExchange();
  ~DataCmdExchange();

  /**
   * @brief Receive feedback data and send command. Remind the update rate between 
   * hardware devices is 500 Hz, that is, the higher rate of your own controller dose 
   * not work actually.
   */
  void receiveData(InputData&);
  void sendCmd(OutputData&);

  /**
   * @brief Verify the connection at the start time.
   */
  bool isConnect();

  /**
   * @brief These 2 functions are utilized to set periodic cycle.
   * If you want to run your algorithm with 500 Hz, the code can be as follow,
   * 
   *    double dt = 0.002;
   *    while (1) {
   *      time_point start = this->initDuration();
   * 
   *      // your algorithm
   * 
   *      this->waitDuration(start, dt);
   *    }
   */
  time_point initDuration();
  void waitDuration(const time_point &t_start, double dt);

  std::shared_ptr<LcmReceiver> receiver;
};

#endif /* _MAGICLAB_QUAD_SDK_DATA_CMD_EXCHANGE_ */