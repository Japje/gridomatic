from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('',
	url(r'^vm/list/$',                     vm_list,    name='vm_list'),
	url(r'^vm/start/$',                    vm_start,   name='vm_start'),
	url(r'^vm/stop/$',                     vm_stop,    name='vm_stop'),
	url(r'^vm/destroy/$',                  vm_destroy, name='vm_destroy'),
	url(r'^vm/restart/$',                  vm_restart, name='vm_restart'),
	url(r'^vm/create/$',                   vm_create,  name='vm_create'),
	url(r'^vm/details/(?P<uuid>[^/]+)/$',  vm_details, name='vm_details'),
	url(r'^vm/edit/(?P<uuid>[^/]+)/$',     vm_edit,    name='vm_edit'),

	url(r'^network/list/$',                    network_list,    name='network_list'),
	url(r'^network/create/$',                  network_create,  name='network_create'),
	url(r'^network/details/(?P<uuid>[^/]+)/$', network_details, name='network_details'),
	url(r'^network/edit/(?P<uuid>[^/]+)/$',    network_edit,    name='network_edit'),
)
