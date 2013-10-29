buffer_pool=$1
password="***"
#install mysql
sudo yum install Percona-Server-shared-55.x86_64 Percona-Server-devel-55.x86_64 Percona-Server-server-55.x86_64 Percona-Server-client-55.x86_64 -y
sudo mkdir -p /opt/local/mysql/var/
sudo mysql_install_db --datadir=/opt/local/mysql/var/
sudo chown -R mysql:mysql /opt/local/mysql/var

#get and modify config
scp dbbk01:~/my.cnf ./
sudo mv my.cnf /etc/my.cnf
server_id=`/sbin/ifconfig|grep inet|grep 10|awk '{print $2}'|awk -F. 'END{printf("%d%03d%03d",$2,$3,$4)}'`
sudo sed -i "s/server_id=[0-9]*/server_id=$server_id/" /etc/my.cnf
sudo sed -i "s/innodb_buffer_pool_size=.*/innodb_buffer_pool_size=$buffer_pool/" /etc/my.cnf

#start mysql
sudo /etc/init.d/mysql start

#drop empty user
mysql -uroot --password="" -S/opt/tmp/mysql.sock -e"drop user ''@'localhost'"
hostname=`hostname`
mysql -uroot --password="" -S/opt/tmp/mysql.sock -e"drop user ''@'$hostname'"

echo "update mysql.user set password=password('$password') where user='root';"|mysql -uroot --password="" -S/opt/tmp/mysql.sock
echo "flush privileges;"|mysql -uroot --password="" -S/opt/tmp/mysql.sock

#admin & superadmin user&replication &monitor user
scp dbbk01:~/tools/grant.sh ./
sh grant.sh
rm -rf grant.sh

#ssh pub key
scp dbbk01:~/.ssh/id_rsa.pub ~/
mkdir -p ~/.ssh
cat ~/id_rsa.pub>>~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
rm -rf ~/id_rsa.pub
