#!/bin/sh
#houjunwei rj03hou@gmail.com
#2013-10-29

redisserver=`ps aux | grep redis-server|grep -v grep`
if [ -n "$redisserver" ];then 
    echo "there is a redis server running,so break"
    exit 1
fi

#install
yum remove redis -y -q
yum install redis -y -q
if [ -d "/opt/local/redis6379" ];then 
    rm -r /opt/local/redis6379
fi

mkdir -p /opt/local/redis6379
chown -R redis:redis /opt/local/redis6379

#ulimit
ulimit_grep=`cat /etc/security/limits.conf |grep "* soft nofile 288000"`
if [ "$ulimit_grep" = "" ] ; then
    echo "* soft nofile 288000">>/etc/security/limits.conf
    echo "* hard nofile 288000">>/etc/security/limits.conf  
    ulimit -n 288000
    sleep 1
fi
ulimit -n

#overcommit_memory
check_proc=`cat /proc/sys/vm/overcommit_memory`
overcommit_grep=`cat /etc/sysctl.conf|grep vm.overcommit_memory=1`
if [ $check_proc -ne 1 -o "$overcommit_grep" = "" ] ; then
    echo "vm.overcommit_memory=1">>/etc/sysctl.conf
    /sbin/sysctl -p  /etc/sysctl.conf
fi
cat /proc/sys/vm/overcommit_memory

#swap
check_swap=`cat /proc/sys/vm/swappiness`
swap_grep=`cat /etc/sysctl.conf|grep vm.swappiness=0`
if [ $check_swap -ne 0 -o "$swap_grep" = "" ] ; then
    echo "vm.swappiness=0">>/etc/sysctl.conf
    /sbin/sysctl -p  /etc/sysctl.conf
fi
cat /proc/sys/vm/swappiness

#set bgrewriteaof
echo "auto-aof-rewrite-percentage 100">>/etc/redis.conf
echo "auto-aof-rewrite-min-size 64mb">>/etc/redis.conf

#change the port
sed -i "s/6389/6379/g" /etc/redis.conf

#start redis
setuidgid redis redis-server /etc/redis.conf

ps aux | grep redis
