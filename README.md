It is built mainly with python 3.5 and flask. This project is not compatible with python 2.7

## Environment preparation.
1. For python3.5, must run ** sudo apt-get install python3.5-dev python3-setuptools ** at first. Otherwise, there will be issue for installing required packages.
2. Highly recommend to use virtualenv or conda for isolating python running environment. 
3. For installation on ubuntu, please run following to install the dependencies
  > sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk libffi-dev libssl-dev python3-dev libmysqlclient-dev

4. For centos
  > sudo yum install libffi-devel mysql-devel python-devel

5. For mysql, please make sure the mysql-devel has version larger than 5.5, otherwise, the utf8mb4 codec cannot be supported! If you re-install mysql-devel after installation of mysqlclient, please uninstall and re-install mysqlclient again without cache enabled. 

6. Install and turn on redis. If you want to use some advanced features of redis, please make sure you install correct redis version.   

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
   
If environment variable changed, you need to restart supervisord in the command line session which contains the changed variable. 

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

## How to expose the api document
Currently, [swagger](http://swagger.io/) is used to generate restful api document auto. [flask-restful-swagger](https://github.com/rantav/flask-restful-swagger) is the module I selected.  
By default, you can access [http://127.0.0.1:5000/api/spec.html](http://127.0.0.1:5000/api/spec.html) to get the list of provided api.  
If it is the first time for you to use swagger, you should read [5.2 API Declaration](http://docs.swagger.io/spec.html) at first. 


## How to have stress test
The stress test used locust as test engine. Please refer the sample within stressTest folder.

## Local environment need to provided during running
Here is the list of needed system environment during running, please check their existence before running.  

* SECRET_KEY: If not provided, a default one will be given.
* **MAIL_USERNAME**: the user mail box login name for sending alert email
* **MAIL_PASSWORD**: the user mail box login password for sending alert email
* **DEV_DATABASE_URL**: if you're in develop mode, need this to specify the data resource.
* **TEST_DATABASE_URL**: if you're in test mode, need this to specify the data resource.
* **DATABASE_URL**: if you're in product mode, need this to specify the data resource.
* FLASK_COVERAGE: By default, it will be treated as enabled to get test code coverage.

## using linux embeded logrotator
To reduce disk space usage by logs, it is recommended to use logrotator for log compression.   
The routine should be set in /etc/logrotate.d. And you can refer [here](http://www.softpanorama.org/Commercial_linuxes/RHEL/rhel_log_rotation.shtml) for details.  
The following sample is a configuration I created which will check log file daily and compress it if log size exceeds 10MB. The maxium retain copies are 20.  

```
/alidata/tk03/wechat/71-wechat-server/logs/*.log {
   daily
   missingok
   size 10M
   copytruncate
   create
   compress
   compresscmd /usr/bin/bzip2
   compressext .bz2
   rotate 20
}
```

It will be a good practice to use random running time to avoid hardware workload. Here is a sample in /etc/anacrontab.

```bash
# the maximal random delay added to the base delay of the jobs
RANDOM_DELAY=45
# the jobs will be started during the following hours only
START_HOURS_RANGE=3-22
```