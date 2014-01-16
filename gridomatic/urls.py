from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('',
	url(r'^vm/list/$',    vm_list,    name='vm_list'),
	url(r'^vm/start/$',   vm_start,   name='vm_start'),
	url(r'^vm/stop/$',    vm_stop,    name='vm_stop'),
	url(r'^vm/restart/$', vm_restart, name='vm_restart'),
	url(r'^vm/create/$',  vm_create,  name='vm_create'),

	url(r'^network/list/$',    network_list,    name='network_list'),
	url(r'^network/create/$',  network_create,  name='network_create'),
)
