# Grid-o-Matic

Webinterface for XenServer

## Installation

	git clone https://github.dtc.avira.com/wiedi/gridomatic.git
	cd gridomatic
	mkvirtualenv gridomatic
	pip install -r req.txt

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

Run worker:

	./manage.py celery worker
