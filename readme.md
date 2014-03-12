# Grid-o-Matic

Webinterface for XenServer

## Supported features:
* Multi server/pool support
* Using xe-automator, provision network, hostname, ssh-key, password and puppet-certs

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
* Select if you want backups (Using XenBackup)
* Set Tags
* Set customfields

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

	git clone https://github.com/Japje/gridomatic.git
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

	apt-get install rabbitmq-server

Start Server for dev:
	
	sudo rabbitmq-server

Sync DB:

	./manage.py syncdb

Run worker:

	./manage.py celery worker


## Ubuntu template addon

See: <https://github.com/Japje/xenserver-automater>

Once these scripts are installed you are able to use all the auto-deployable functionality of the grid-o-matic


## Customfields and Tags

Unfortunately, the xenapi has no grouping for tags and/or customfields. This means i had to come up with a way to see which tags/fields excist in a hacky way:
For each tag you want available for a pool, you should SET the tag on the pool object.
for each custom field you want available, you sould fill in the custom field on the pool object with the text 'not set'


# networks
To reduce the amount of work while creating a VM i have removed gateway, subnet and DNS from the creation form.

These will now be pulled from the network object itself via a custom field.

For each network you want to use set the following customfields:

network.ipv4
network.ipv6
network.dns


Syntax for the network information is | (pipe) seperated:
192.168.1.1|255.255.255.0 (gateway|netmask)
or for IPv6
2001:db8:1337::1|64

The syntax for the DNS is space seperated:
8.8.8.8 8.8.4.4
