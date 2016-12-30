It is built mainly with python 3.5 and flask and not compatible with python 2.7

## Environment preparation.
1. For python3.5, must run ** sudo apt-get install python3.5-dev python3-setuptools ** at first. Otherwise, there will be issue for installing required packages.
2. Highly recommend to use virtualenv or conda for isolating python running environment. 
3. For installation on ubuntu, please run following to install the dependencies
  > sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk libffi-dev libssl-dev python3-dev libmysqlclient-dev

4. For centos
  > sudo yum install libffi-devel mysql-devel python-devel

5. For mysql, please make sure the mysql-devel has version larger than 5.5, otherwise, the utf8mb4 codec cannot be supported! If you re-install mysql-devel after installation of mysqlclient, please uninstall and re-install mysqlclient again. 

6. Install redis and turn on. If you want to use some advanced features of redis, please make sure you install correct redis version.   

  * yum install redis
  * sudo /etc/init.d/redis start  
  * sudo /sbin/chkconfig redis on
  
7. Install Supervisor. It will use python 2.7 instead.

  * sudo pip install supervisor
  
## How to run
* use flask default one:  
> python manager.py runserver   

* use to start the gunicorn version:  
> **gunicorn -c gunicorn.conf manager:flask_app**  # recommended one   

* for public release, recommend to use supervisor to run this app:  
> 1. **supervisord** (once only to make sure the server is run)  
> 2. supervisorctl reread  (only needed if configuration changed)  
> 3. supervisorctl update  (only needed if configuration changed)  
> 4. supervisorctl status backend  (check the status is running)  
> 5. supervisorctl status celery  (check the status is running)  

if you want to restart one in case there is code change, run  
> supervisorctl restart backend  
> supervisorctl restart celery  
 

## How to upgrade DB  

1. python manager.py db migrate
2. change the generate py file manually, EG, to add index because it does not support. 
3. python manager.py db upgrade

Alembic record the latest version in db. Therefore, be careful!

## How to test functionality  
The test code should be within tests folder and an example is provided there.

1. Have your test db created. Recommend mysql. It should sth like   
> TEST_DATABASE_URL="mysql://test:test@192.168.0.106/wechat_habit_test?charset=utf8mb4"  

2. run 
> python manager.py test  

3. Check result. All should pass

## How to have stress test
The stress test used locust as test engine. Please refer the sample within stressTest folder.