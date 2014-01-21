from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.conf import settings
from forms import *
from .xen import Xen
import json
import tasks

def vm_list(request):
	return render(request, 'gridomatic/vm_list.html', {'vms': Xen().vm_list()})

def vm_details(request, uuid):
	details  = Xen().vm_details(uuid)
	networks = Xen().network_names(details['VIFs']) 
	disks    = Xen().disks_by_vdb(details['VBDs']) 
	
	return render(request, 'gridomatic/vm_details.html', {'details': details, 'networks': networks, 'disks': disks})

def vm_edit(request, uuid):
	details = Xen().vm_details(uuid)
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
		Xen().vm_update(uuid, form.cleaned_data)
		return redirect('vm_details', uuid )

	return render(request, 'gridomatic/vm_edit.html', {'details': details, 'form': form})

def vm_start(request):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_start.delay(uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

def vm_stop(request):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_stop.delay(uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

def vm_destroy(request):
	if request.method == "POST":
		uuid = request.POST.get('uuid', None)
		Xen().vm_destroy(uuid)
		return redirect('vm_list')
	else:
		return HttpResponseNotAllowed('Only POST here')

def vm_restart(request):
	uuid = request.POST.get('uuid', None)
	task_id = tasks.vm_restart.delay(uuid).id
	return HttpResponse(json.dumps({'task_id': task_id}), content_type="application/json")

def vm_create(request):
	form = VMCreateForm(request.POST or None)
	x = Xen()
	form.fields['network'].choices  = x.get_network_list()
	form.fields['template'].choices = x.get_template_list()
	form.fields['host'].choices     = x.get_host_list()

	if form.is_valid():
		task_id = tasks.vm_deploy.delay(form.cleaned_data).id
		return render(request, 'gridomatic/vm_create_wait.html', {'form': form, 'task_id': task_id})
	return render(request, 'gridomatic/vm_create.html', {'form': form})

def network_list(request):
	network_list = Xen().network_list_dev()
	return render(request, 'gridomatic/network_list.html', {'networks': network_list})

def network_create(request):
	form = NetworkCreateForm(request.POST or None)

	if form.is_valid():
		Xen().network_create(form.cleaned_data)
		return redirect('network_list')
	return render(request, 'gridomatic/network_create.html', {'form': form})

def network_details(request, uuid):
	details = Xen().network_details(uuid)
	vifs = details['VIFs']
	vms = Xen().vmnames_by_vif(vifs) 
	return render(request, 'gridomatic/network_details.html', {'details': details, 'vms': vms })


def network_edit(request, uuid):
	details = Xen().network_details(uuid)
	form = NetworkEditForm(request.POST or None, initial={
		'name': details['name_label'],
		'description': details['name_description'],
		'racktables_id': details['other_config']['racktables_id'],
	})

	if form.is_valid():
		Xen().network_update(uuid, form.cleaned_data)
		return redirect('network_details', uuid )

	return render(request, 'gridomatic/network_edit.html', {'details': details, 'form': form})
