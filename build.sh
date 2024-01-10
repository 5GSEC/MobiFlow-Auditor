#!/usr/bin/env bash
sudo apt-get install -y gcc-multilib flex csh

_OS_SYSN=$(uname -s | tr "-" "_")
_OS_VERS=$(uname -r | cut -d. -f1-2 | cut -d- -f1)
_OS_VERS_STR=$(uname -r | cut -d. -f1-2 | cut -d- -f1 | tr '.' '_')
_OS_ARCH=$(uname -m | sed 's/ /_/g')
_OS_NAME="${_OS_SYSN}-${_OS_VERS}"
_OS_NAME_ARCH="${_OS_SYSN}-${_OS_ARCH}"

#if [ ! -d "./mobiflow-auditor/pbest/pbcc/$_OS_NAME_ARCH" ]; then
#  echo "Compiling pbcc"
#  pushd ./mobiflow-auditor/pbest/pbcc && make && popd
#fi
#
#if [ ! -d "./mobiflow-auditor/pbest/libpb/$_OS_NAME_ARCH" ]; then
#  echo "Compiling libpb"
#  pushd ./mobiflow-auditor/pbest/libpb && make && popd
#fi
#
#(pushd ./mobiflow-auditor/pbest/expert && make clean && make && popd)

sudo make image/mobiflow-auditor
sudo docker push localhost:5000/mobiflow-auditor
