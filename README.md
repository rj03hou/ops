##zabbix.py
* config

    用于存储配置项
* log

    简单的log模块
* Zabbixtools
    
    对zabbix常用的操作进行了封装。
    
* set_db_group_and_template
    
    调用Zabbixtools的API，初始化数据库时设置服务器的group和template。

* calc_all_db_group_disk_consume

    调用Zabbixtools的API，计算某个服务组中的机器的磁盘消耗趋势，得出多久之后服务器的磁盘空间将消耗殆尽，可以提前给出实际的容量预估。