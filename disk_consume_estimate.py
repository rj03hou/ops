#!/usr/bin/env python
# -*- coding: utf-8 -*-
#houjunwei rj03hou@gmail.com
#2013-10-24
#base from http://wangwei007.blog.51cto.com/68019/1249770
#The API document https://www.zabbix.com/documentation/1.8/api

import json
import urllib2
import sys
import time

class Config:
    log_level = "ERROR"
    zabbix_url = "http://zabbix.xxx.com/api_jsonrpc.php"
    zabbix_user = "sys"
    zabbix_password = ""
    groupname = "db"
    #the disk corresponding zabbix item key.
    disk_item_key = "vfs.fs.size[/opt,free]"
    #to calc the disk increase speed, we must get the item value somes days.
    get_value_days = 10


class log:
    @classmethod
    def debug(self,message):
	if "DEBUG" == Config.log_level:
	    print message


class Zabbixtools:
    def __init__(self):
        self.url = Config.zabbix_url
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": Config.zabbix_user,
                        "password": Config.zabbix_password
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "Auth Failed, Please Check Your Name And Password:",e.code
        else:
            response = json.loads(result.read())
            result.close()
            authID = response['result']
            return authID

    def get_data(self,data,hostip=""):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
            return 0
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def hostgroup_get_id(self,groupname):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output":"shorten",
                        "filter": {"name": [groupname]}
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
	log.debug(groupname)
	log.debug(res)
        if (res != 0) and (len(res) == 1):
            group = res[0]
	    log.debug(group['groupid'])
	    return group['groupid']
        else:
	    return -1

    def host_get_by_groupid(self,groupid):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output":"shorten",
			"groupids":groupid,
                        },
                    "auth": self.authID,
                    "id": 1,
                })
        res = self.get_data(data)['result']
	log.debug(groupid)
	log.debug(res)
	return res

    def get_hostname_by_hostid(self,hostid):
	log.debug("##get_hostname_by_hostid")
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output":"extend",
			"hostids":[hostid],
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
	log.debug(hostid)
	log.debug(res)
	
        if (res != 0) and (len(res) == 1):
            host = res[0]
	    hostname = host['host']
	    log.debug(hostname)
	    return hostname
        else:
	    raise Exception("can't found hostname",hostid)

    def host_get(self,hostname):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output":"extend",
                        "filter": {"host": [hostname]}
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
	log.debug(hostname)
	log.debug(res)
	return res

    def host_get_id(self,hostname):
	res = self.host_get(hostname)
        if (res != 0) and (len(res) == 1):
            host = res[0]
	    log.debug(host['hostid'])
	    return host['hostid']
        else:
	    return -1
	
    def history_get(self,itemid,time_from):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "history.get",
                    "params": {
			"itemids": [itemid],
			"time_from": time_from,
                        "output": "extend",
			"sortorder": "ASC",
			"limit": "1"
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
	log.debug(res)
        if (res != 0) and (len(res) == 1):
	    return res[0]
	else:
	    return {"value":-1,"clock":time_from}

    def item_get_id(self,hostid,item_key):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
			"hostids": [hostid],
                        "output": "shorten",
			"search": {"key_":item_key}
                        },
                    "auth": self.authID,
                    "id": 1
                })
        res = self.get_data(data)['result']
	log.debug(res)
	if(len(res) == 1):
	    return res[0]["itemid"]
        else:
	    return -1

    def get_host_disk_consume(self,hostid):
	log.debug("##get_host_disk_consume")
	#wtf, because the mount dir is not uniform.
	item_key = "vfs.fs.size[/opt/local/mysql/var,free]"
	item_id = self.item_get_id(hostid,item_key)
	if -1 == item_id:
	    item_key = Config.disk_item_key
	    item_id = self.item_get_id(hostid,item_key)
	    if -1 == item_id:
		raise Exception("can't get item_id")
	
	DIFF_COUNT = Config.get_value_days
	values=[]
	now_ts = time.time()
	for i in range(0,DIFF_COUNT):
	    #because now maybe zabbix hasn't get the value, so we just subtract 600s
	    from_ts = now_ts - 600 - 24*60*60*i
	    res = self.history_get(item_id,from_ts)
	    values.append(res)
	    if(i!=0):
		values[i]["diff"] = int(values[i]["value"]) - int(values[i-1]["value"])

	begin = int(values[1]["value"])
	end = int(values[DIFF_COUNT-1]["value"])

	diffs=[]	
	for i in range(1,DIFF_COUNT):
	    log.debug(values[i]["diff"])
	    diffs.append(values[i]["diff"])

	#remove the biggest and the smallest value and the negative from diff
	diffs.sort() 
	sum = 0
	count = 0
	log.debug("get the avg diff")
	for i in range(0,len(diffs)-2):
	    if(diffs[i]>0):
		log.debug(diffs[i])
		sum += diffs[i]
		count += 1
	#if the decrease if more than increase, maybe they have a crontab to relase space.
	#like this 5 4 5 4 5 4
	if(count>0 and count>(DIFF_COUNT-2)*0.5):
	    avg = sum*1.0/count
	    #In theory (end-begin)=avg*DIFF_COUNT,
	    #but if the diff is small than the theory*0.3, something maybe wrong.
	    #this may not valid, because may just release some space in the middle like db-db206.
	    #like this:5 4 3 10 9 8 7 6
	    """
	    if (end-begin) < avg*DIFF_COUNT*0.3:
		days = -1
	    else:
	    	log.debug(avg)
	    	days = int(values[0]["value"])/avg
	    """
	    log.debug(avg)
	    days = int(values[0]["value"])/avg
	else:
	    days = -1
	log.debug(days)
	return int(days) 


def test():
    zb = Zabbixtools()
    hostid=zb.host_get_id("db1")
    days = zb.get_host_disk_consume(hostid)
    print "db1",days


def main():
    zb = Zabbixtools()
    groupid = zb.hostgroup_get_id(Config.groupname)
    res = zb.host_get_by_groupid(groupid)
    host_days=[]
    for host in res:
	hostid = host["hostid"]
	hostname = zb.get_hostname_by_hostid(hostid)
	days = zb.get_host_disk_consume(hostid)
	host_days.append({"hostname":str(hostname),"days":days})

    sorted_host_days =  sorted(host_days, key = lambda x:x['days'])
    for host in sorted_host_days:
	if -1 != host["days"]:
	    print host["hostname"],host["days"]

    
if __name__ == "__main__":
    main()
    #test()
