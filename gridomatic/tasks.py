from __future__ import absolute_import
from celery import shared_task
from .xen import *

@shared_task
def vm_start(uuid):
	Xen().vm_start(uuid)

@shared_task
def vm_stop(uuid):
	Xen().vm_stop(uuid)

@shared_task
def vm_restart(uuid):
	Xen().vm_restart(uuid)

@shared_task
def vm_destroy(uuid):
	Xen().vm_destroy(uuid)
