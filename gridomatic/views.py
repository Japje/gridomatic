from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.util import ValidationError
from operator import itemgetter
from collections import OrderedDict
from forms import *
from .xen import Xen
import json
import tasks
import string
import random

def gen_password(size=24, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

# Check if big list contains all items in small list
def contains(small, big):
	for item in small:
		if not item in big:
			return False
	return True


# check if network supports ipv6
def network_has_ipv6(poolname, network_uuid, ipv6_addr = None):
	if not ipv6_addr:
		return True
	else:
		network_details = Xen(poolname).network_details_uuid(network_uuid)
		if not 'XenCenter.CustomFields.network.ipv6' in network_details['other_config']:
			return False
	return True


# mainpage

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

# vm views

@login_required
def vm_list_combined(request):

	data = []
	listtags = []
	pools = settings.XENPOOLS

	filtertags = request.POST.getlist("tags")

	form = TagsForm(request.POST or None)
	for poolname in pools:
		tags = Xen(poolname).get_tags()
		for tag in tags:
			listtags += [( tag, tag )]

		vms = Xen(poolname).vm_list()

		for ref,vm in vms.items():
			if vm["is_a_template"] or vm['is_a_snapshot'] or vm["is_control_domain"]: continue

			if contains(filtertags, vm['tags']):
				data += [{
					'name':        vm['name_label'],
					'power_state': vm['power_state'],
					'uuid':        vm['uuid'],
					'poolname': poolname,
				}]

	sorted_data = sorted(data, key=itemgetter('name'))

	listtags = list(set(listtags))
	form.fields['tags'].choices = sorted(listtags)

	if 'json' in request.REQUEST:
		return HttpResponse(json.dumps({'vmlist': sorted_data}), content_type = "application/json")
	else:
		return render(request, 'gridomatic/vm_list.html', {'vmlist': sorted_data, 'form': form})


@login_required
def vm_details(request, poolname, uuid):
	details  = Xen(poolname).vm_details(uuid)

	if details['power_state'] == 'Running':
		host  = Xen(poolname).host_details(details['resident_on'])
	else:
		host  = {'name_label': 'Not implemented for stopped VMs yet'}

	customfield = {}

	for item in details['other_config']:
		if 'XenCenter.CustomFields' not in item: continue
		field = str(item.split('.')[2])
		value = str(details['other_config'][item])

		customfield[field] = value

	data = []
	data += [{
			'name': details['name_label'],
			'description': details['name_description'],
			'poolname': poolname,
			'host':  host['name_label'],
			'uuid':  details['uuid'],
			'powerstate':  details['power_state'],
			'vcpus':  details['VCPUs_at_startup'],
			'memory': details['memory_static_max'],
			'tags': details['tags'],
			'disks': Xen(poolname).disks_by_vdb(details['VBDs']),
			'networks': Xen(poolname).network_details_ref(details['VIFs']),
			'customfield':  customfield,
	}]

	if 'json' in request.REQUEST:
		return HttpResponse(json.dumps({'vmdetails': data}), content_type = "application/json")
	else:
		return render(request, 'gridomatic/vm_details.html', {'vmdetails': data})


@login_required
def vm_edit(request,  poolname, uuid):
	details = Xen(poolname).vm_details(uuid)
	backup = False
	pooltags = []

	tags = Xen(poolname).get_tags()
	for tag in tags:
		pooltags += [( tag, tag )]

	pooltags = list(set(pooltags))
	vmtags   = details['tags']
	customfield = {}


	# populate all possible customfields to show empty fields
	poolcustomfields = Xen(poolname).get_other_config()
	for item in poolcustomfields:
		if 'XenCenter.CustomFields' not in item: continue
		field = str(item.split('.')[2])
		value = poolcustomfields[item]
		if value == 'not set':
			customfield[field] = value

	# fill the custom fields with already excisting data
	for item in details['other_config']:
		if 'XenCenter.CustomFields' not in item: continue
		field = str(item.split('.')[2])
		value = str(details['other_config'][item])
		customfield[field] = value


	# We want a fancy select box for this one
	del customfield['backup']

	if 'XenCenter.CustomFields.backup' in details['other_config']:
		if details['other_config']['XenCenter.CustomFields.backup'] == '1':
			backup = True


	form = VMEditForm(request.POST or None, extra=customfield ,initial={
		'description': details['name_description'],
		'cpu_cores':   details['VCPUs_at_startup'],
		'backup':      backup,
		'mem_size':    int(details['memory_static_max'])/1024/1024,
		'tags':        vmtags,
	})

	if details['power_state'] == 'Running':
		form.fields['mem_size'].widget.attrs['readonly'] = True
		form.fields['cpu_cores'].widget.attrs['readonly'] = True

	form.fields['tags'].choices = sorted(pooltags)

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
	customfield = {}

	# populate all possible customfields to show empty fields
	poolcustomfields = Xen(poolname).get_other_config()
	for item in poolcustomfields:
		if 'XenCenter.CustomFields' not in item: continue
		field = str(item.split('.')[2])
		value = poolcustomfields[item]
		if value == 'not set':
			customfield[field] = ""

	# We want a fancy select box for this one
	del customfield['backup']

	form = VMCreateForm(request.POST or None, extra=customfield, initial={'password': gen_password()} )
	x = Xen(poolname)
	networks = x.network_list()	
	network_list = []

	for net in networks:
		if not 'Production' in networks[net]['tags']: continue
		network_list += [(
			networks[net]['uuid'], 
			networks[net]['name_label']
		)]

	masters = settings.PUPPETMASTERS
	puppetmaster_list = []
	for master in masters:
		puppetmaster_list += [(
			masters[master]['hostname'],
			master,
		)]

	pooltags = []

	tags = Xen(poolname).get_tags()
	for tag in tags:
		pooltags += [( tag, tag )]

	pooltags = list(set(pooltags))
	network_list_sorted = sorted(network_list, key=lambda x: x[1])

	form.fields['network'].choices      = network_list_sorted
	form.fields['template'].choices     = sorted(x.get_template_list())
	form.fields['host'].choices         = sorted(x.get_host_list(), reverse=True)
	form.fields['puppetmaster'].choices = sorted(puppetmaster_list)

	form.fields['tags'].choices = sorted(pooltags)


	if request.method == 'POST':
		if not network_has_ipv6(poolname, request.POST['network'], request.POST['ip_address6']):
			form.errors['ip_address6'] = 'Selected Network has no IPv6 support!'

	if form.is_valid():
		task_id = tasks.vm_deploy.delay(poolname,form.cleaned_data).id
		return render(request, 'gridomatic/vm_create_wait.html', {'form': form, 'task_id': task_id, 'poolname': poolname})

	return render(request, 'gridomatic/vm_create.html', {'form': form, 'poolname': poolname})


# Network views

@login_required
def network_list_combined(request):
	data = []
	listtags = []
	filtertags = request.POST.getlist("tags")

	pools = settings.XENPOOLS

	form = TagsForm(request.POST or None)

	for poolname in pools:
		tags = Xen(poolname).get_tags()
		for tag in tags:
			listtags += [( tag, tag )]

		networks = Xen(poolname).network_list()
		for ref, net in networks.items():

			if not net['tags']: continue
			if contains(filtertags, net['tags']):

				data += [{
					'name':        net['name_label'],
					'description': net['name_description'],
					'uuid':        net['uuid'],
					'poolname':    poolname,
				}]

	listtags = list(set(listtags))
	form.fields['tags'].choices = sorted(listtags)

	sorted_data = sorted(data, key=itemgetter('name'))
	if 'json' in request.REQUEST:
		return HttpResponse(json.dumps({'networklist': sorted_data }), content_type = "application/json")
	else:
		return render(request, 'gridomatic/network_list.html', {'networklist': sorted_data, 'form': form })


@login_required
def network_create(request, poolname):
	form = NetworkCreateForm(request.POST or None)

	if form.is_valid():
		Xen(poolname).network_create(form.cleaned_data)
		return redirect('network_list_combined')
	return render(request, 'gridomatic/network_create.html', {'form': form})


@login_required
def network_details(request, poolname, uuid):
	details = Xen(poolname).network_details_uuid(uuid)
	vifs = details['VIFs']
	vms = Xen(poolname).vmdetails_by_vif(vifs)
	data = []

	if 'XenCenter.CustomFields.network.ipv6' in details['other_config']:
		ipv6_gateway = str(details['other_config']['XenCenter.CustomFields.network.ipv6']).split('|', 2)[0]
		ipv6_netmask = str(details['other_config']['XenCenter.CustomFields.network.ipv6']).split('|', 2)[1]
	else:
		ipv6_gateway = ""
		ipv6_netmask = ""

	get_vlan = Xen(poolname).pif_details(details['PIFs'][0])

	data += [{
         'name': details['name_label'],
         'description': details['name_description'],
			'ipv4_gateway':  str(details['other_config']['XenCenter.CustomFields.network.ipv4']).split('|', 2)[0],
			'ipv4_netmask':  str(details['other_config']['XenCenter.CustomFields.network.ipv4']).split('|', 2)[1],
			'ipv6_gateway':  ipv6_gateway,
			'ipv6_netmask':  ipv6_netmask,
			'dns_servers':    str(details['other_config']['XenCenter.CustomFields.network.dns']),
			'VLAN':  get_vlan['VLAN'],
			'uuid':  details['uuid'],
			'mtu':  details['MTU'],
			'tags':  details['tags'],
			'vms': vms,
			'poolname': poolname,
	}]

	if 'json' in request.REQUEST:
		return HttpResponse(json.dumps({'networkdetails': sorted(data)}), content_type = "application/json")
	else:
		return render(request, 'gridomatic/network_details.html', {'networkdetails': sorted(data)})


@login_required
def network_edit(request, poolname, uuid):
	details = Xen(poolname).network_details_uuid(uuid)
	form = NetworkEditForm(request.POST or None, initial={
		'name': details['name_label'],
		'description': details['name_description'],
	})

	if form.is_valid():
		Xen(poolname).network_update(uuid, form.cleaned_data)
		return redirect('network_details', poolname, uuid )

	return render(request, 'gridomatic/network_edit.html', {'details': details, 'form': form, 'poolname': poolname})
