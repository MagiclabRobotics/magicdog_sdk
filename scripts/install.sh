#!/bin/bash

directory="/usr/local/include/magiclab_sdk"

if [ ! -d "$directory" ]; then
  sudo mkdir "$directory"
fi

sudo cp ../lib/libmagiclab_mjr_sdk_x86.a /usr/local/lib
sudo cp ../include/common.h /usr/local/include/magiclab_sdk
sudo cp ../include/DataCmdExchange.h /usr/local/include/magiclab_sdk/
