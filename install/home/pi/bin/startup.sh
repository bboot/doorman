#!/bin/bash

# usage: get_pid <binary> <unique param>
get_pid() {
    local is_running=$(pgrep -a $1 | grep $2)
    if [ "$is_running" != "" ]; then
        pid=($is_running)
        pid=${pid[0]}
        echo "$pid"
    fi
}

# usage: wait_on <binary> <unique param> <wait time>
wait_on() {
    pid=`get_pid $1 $2`
    i=0
    while [ "$pid" == "" -a $i -lt $3 ]; do
        sleep 1
        i=$[$i+1]
        pid=`get_pid $1 $2`
    done
}

if [ "`whoami`" == "root" ]; then
    # likely just booted up.  wait for services to be ready
    # wait for lxsession to be running before continuing
    `wait_on lxsession lxsession 25`
    # re-run as user pi
    su pi -c $0
    exit
fi

pid=`get_pid python voice-recognizer-raspi`
if [ "$pid" != "" ]; then
    echo Already running in pid $pid
    exit
fi

LOG=/home/pi/logs/voice-recognizer.log
. /etc/bash.bashrc
. /home/pi/.bashrc

cat /etc/aiyprojects.info

cd /home/pi/voice-recognizer-raspi
. /home/pi/voice-recognizer-raspi/env/bin/activate
echo ++++++++++++++++++++++++ NEW LOG START $(date) >> $LOG
#trigger=clap
trigger=gpio
/home/pi/voice-recognizer-raspi/doorman/main.py --cloud-speech --trigger=$trigger >> $LOG 2>&1 &
