# Grid-o-Matic

Webinterface for XenServer

## Supported features:
* Limited to a single server or pool
* Using xe-automator, provision network, hostname, ssh-key, puppet-certs

##### List running VM's
* Filtered by tag(s)

##### Actions
* Start/Stop/Restart/Edit/Destroy VM's


##### Create new VM:
* Set static IP for VM
* Set static IPv6 for VM (limited)             
* Select template (only ubuntu 12.04 LTS for now)
* Select network
* Select host (if in pool)
* Set Memory amount      
* Set vCPU amount
* Set SSH key for user root

##### Edit VM:
* Description
* Memory Size
* vCPU amount

##### Create new Network:
* Name
* Description
* Vlan

##### Edit Network:
* Name
* Description

## Installation

	git clone https://github.dtc.avira.com/japje/gridomatic.git
	cd gridomatic
	mkvirtualenv gridomatic
	pip install -r req.txt

After this you can create the gridomatic_web/local_settings.py with the settings needed for your server/pool

## Dev Server

	./manage.py runserver

## Celery

See: <http://docs.celeryproject.org/en/master/getting-started/brokers/rabbitmq.html>

On OSX:

	brew install rabbitmq

On Ubuntu:

	apt-get install rabbitmq

Start Server for dev:
	
	sudo rabbitmq-server

Sync DB:

	./manage.py syncdb

Run worker:

	./manage.py celery worker


## Ubuntu template addon

See: <https://github.com/Japje/xenserver-automater>

Once these scripts are installed you are able to use all the auto-deployable functionality of the grid-o-matic
