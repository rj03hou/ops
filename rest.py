#!/usr/bin/python
#houjunwei@meituan
#2013-10-21

import web
import MySQLdb
import json
from zabbix import *

urls = (
    '/db/(.+)/(\d+)', 'get_db',
    '/table/(.+)/(\d+)/(.+)', 'get_table',
    '/initialzb/(.+)/(.+)', 'initial_zb'
)

app = web.application(urls, globals())
web.config.debug = False

def get_cursor(ip,port,db):
    user = "admin"
    passwd = "XXX"
    conn = MySQLdb.connect(host=ip,port=int(port),user=user,passwd=passwd,db=db,charset='utf8')
    cursor = conn.cursor()
    cursor.execute('set autocommit=1')
    return conn,cursor


class get_db:        
    def GET(self,ip,port):
	dbs=[]
	conn,cursor = get_cursor(ip,port,"test")
	cursor.execute("show databases;")
	for db, in cursor.fetchall():
	    dbs.append(str(db))
	cursor.close()
	conn.close()
        return json.dumps(dbs)

class get_table:        
    def GET(self,ip,port,db):
	tables=[]
	conn,cursor = get_cursor(ip,port,db)
	cursor.execute("show tables;")
	for table, in cursor.fetchall():
	    tables.append(str(table))
	cursor.close()
	conn.close()
        return json.dumps(tables)

class initial_zb:
    def GET(self,host,group):
	res = set_db_group_and_template(host,group)
	return res

if __name__ == "__main__":
    app.run()
