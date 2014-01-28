from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('',
	url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'gridomatic/login.html'}),

	url(r'^$',                     index,    name='index'),

	url(r'^pool/(?P<poolname>[^/]+)/vm/list/$',                     vm_list,    name='vm_list'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/start/$',                    vm_start,   name='vm_start'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/stop/$',                     vm_stop,    name='vm_stop'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/destroy/$',                  vm_destroy, name='vm_destroy'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/restart/$',                  vm_restart, name='vm_restart'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/create/$',                   vm_create,  name='vm_create'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/details/(?P<uuid>[^/]+)/$',  vm_details, name='vm_details'),
	url(r'^pool/(?P<poolname>[^/]+)/vm/edit/(?P<uuid>[^/]+)/$',     vm_edit,    name='vm_edit'),

	url(r'^pool/(?P<poolname>[^/]+)/network/list/$',                    network_list,    name='network_list'),
	url(r'^pool/(?P<poolname>[^/]+)/network/create/$',                  network_create,  name='network_create'),
	url(r'^pool/(?P<poolname>[^/]+)/network/details/(?P<uuid>[^/]+)/$', network_details, name='network_details'),
	url(r'^pool/(?P<poolname>[^/]+)/network/edit/(?P<uuid>[^/]+)/$',    network_edit,    name='network_edit'),
)
