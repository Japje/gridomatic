from __future__ import absolute_import
from celery import shared_task
from .xen import *

@shared_task
def vm_start(poolname,uuid):
	Xen(poolname).vm_start(uuid)

@shared_task
def vm_stop(poolname,uuid):
	Xen(poolname).vm_stop(uuid)

@shared_task
def vm_restart(poolname,uuid):
	Xen(poolname).vm_restart(uuid)

@shared_task
def vm_destroy(poolname,uuid):
	Xen(poolname).vm_destroy(uuid)

@shared_task
def vm_deploy(poolname,options):
	Xen(poolname).vm_deploy(options)
