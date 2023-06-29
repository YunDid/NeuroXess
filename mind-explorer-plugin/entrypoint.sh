#!/bin/bash

PYTHON=python3

# 设置一个在项目根目录且唯一的文件，用于定位根目录
BUILD_REQUIREMENT="requirements.txt"

# 定位根目录
ROOT_PATH=$(cd `dirname $0`; pwd)
echo $ROOT_PATH
cd $ROOT_PATH
if [ ! -z $BUILD_REQUIREMENT ]; then
  for ((i=0; i<=5; i++)); do
    if [ -f $BUILD_REQUIREMENT ]; then
      echo "Get project root path:`pwd`"
      ROOT_PATH=`pwd`
      break
    else
      cd ../
    fi
  done
fi

cd $ROOT_PATH
echo $ROOT_PATH
export PYTHONPATH=$ROOT_PATH

ENV_CONFIG=./resources/conf/env.conf
if test -f "$ENV_CONFIG"; then
    echo "source config file: $ENV_CONFIG"
    source $ENV_CONFIG
    echo "CACHE_REDIS_HOST: $CACHE_REDIS_HOST"
fi

# 非 docker 环境的 venv
if test -f venv/bin/activate; then
  echo "source venv/bin/activate"
  source venv/bin/activate
  pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
  pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
#  $PYTHON setup.py develop
fi

$PYTHON app/main.py $*
