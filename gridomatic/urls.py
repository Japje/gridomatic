from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('',
	url(r'^list/$',    vm_list,    name='vm_list'),
	url(r'^start/$',   vm_start,   name='vm_start'),
	url(r'^stop/$',    vm_stop,    name='vm_stop'),
	url(r'^restart/$', vm_restart, name='vm_restart'),
	url(r'^create/$',  vm_create,  name='vm_create'),
)

