from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.conf import settings
from forms import *
from .xen import Xen
import json
import tasks

def index(request):
	pools = settings.XENPOOLS
	host_list = []
	for poolname in pools:
		hosts = Xen(poolname).get_host_list()
		host_list += [{
			'pool':  poolname,
		}]
		for host in hosts:
			host_list += [{
					'host':     host[0],
			}]
	return render(request, 'gridomatic/index.html', {'hosts': host_list})

@login_required
def vm_list(request,poolname):
	return render(request, 'gridomatic/vm_list.html', {'vms': Xen(poolname).vm_list(), 'poolname': poolname})

@login_required
def vm_details(request, poolname, uuid):
	details  = Xen(poolname).vm_details(uuid)
	networks = Xen(poolname).network_names(details['VIFs']) 
	disks    = Xen(poolname).disks_by_vdb(details['VBDs']) 
	
	return render(request, 'gridomatic/vm_details.html', {'details': details, 'networks': networks, 'disks': disks, 'poolname': poolname})

@login_required
def vm_edit(request,  poolname, uuid):
	details = Xen(poolname).vm_details(uuid)
	backup = False

	if 'XenCenter.CustomFields.backup' in details['other_config']:
		if details['other_config']['XenCenter.CustomFields.backup'] == '1':
			backup = True

	form = VMEditForm(request.POST or None, initial={
		'description': details['name_description'],
		'cpu_cores':   details['VCPUs_at_startup'],
		'backup':      backup,
		'mem_size':    int(details['memory_static_max'])/1024/1024,
	})

	if form.is_valid():
		Xen(poolname).vm_update(uuid, form.cleaned_data)
		return redirect('vm_details', poolname, uuid )

	return render(request, 'gridomatic/vm_edit.html', {'details': details, 'form': form, 'poolname': poolname})

@login_required
def vm_start(request, poolname):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_start.delay(poolname,uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

@login_required
def vm_stop(request, poolname):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_stop.delay(poolname,uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

@login_required
def vm_destroy(request, poolname):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_destroy.delay(poolname,uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

@login_required
def vm_restart(request, poolname):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_restart.delay(poolname,uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

@login_required
def vm_create(request, poolname):
	form = VMCreateForm(request.POST or None)
	x = Xen(poolname)
	form.fields['network'].choices  = x.get_network_list()
	form.fields['template'].choices = x.get_template_list()
	form.fields['host'].choices     = x.get_host_list()

	if form.is_valid():
		task_id = tasks.vm_deploy.delay(poolname,form.cleaned_data).id
		return render(request, 'gridomatic/vm_create_wait.html', {'form': form, 'task_id': task_id, 'poolname': poolname})
	return render(request, 'gridomatic/vm_create.html', {'form': form, 'poolname': poolname})

@login_required
def network_list(request, poolname):
	network_list = Xen(poolname).network_list_dev()
	return render(request, 'gridomatic/network_list.html', {'networks': network_list, 'poolname': poolname})

@login_required
def network_create(request, poolname):
	form = NetworkCreateForm(request.POST or None)

	if form.is_valid():
		Xen(poolname).network_create(form.cleaned_data)
		return redirect('network_list')
	return render(request, 'gridomatic/network_create.html', {'form': form})

@login_required
def network_details(request, poolname, uuid):
	details = Xen(poolname).network_details(uuid)
	vifs = details['VIFs']
	vms = Xen(poolname).vmnames_by_vif(vifs) 
	return render(request, 'gridomatic/network_details.html', {'details': details, 'vms': vms, 'poolname': poolname })


@login_required
def network_edit(request, poolname, uuid):
	details = Xen(poolname).network_details(uuid)
	form = NetworkEditForm(request.POST or None, initial={
		'name': details['name_label'],
		'description': details['name_description'],
		'racktables_id': details['other_config']['racktables_id'],
	})

	if form.is_valid():
		Xen(poolname).network_update(uuid, form.cleaned_data)
		return redirect('network_details', poolname, uuid )

	return render(request, 'gridomatic/network_edit.html', {'details': details, 'form': form, 'poolname': poolname})
