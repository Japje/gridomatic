from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
import XenAPI
from forms import VMCreateForm
from .xen import *

def vm_list(request):
	return render(request, 'gridomatic/vm_list.html', {'vms': Xen().vm_list()})

def vm_start(request):
	uuid = request.POST.get('uuid', None)
	Xen().vm_start(uuid)
	return redirect('vm_list')

def vm_stop(request):
	uuid = request.POST.get('uuid', None)
	Xen().vm_stop(uuid)
	return redirect('vm_list')

def vm_restart(request):
	uuid = request.POST.get('uuid', None)
	Xen().vm_restart(uuid)
	return redirect('vm_list')

def deploy(name, ip, gw, netmask, ns, network, template, host, ip6, gw6, netmask6, sshkey):
	import subprocess, os
	(name, domain) = name.split('.', 1)

	env = os.environ.copy()
	env['VMNAME']      = name
	env['VMIP']        = ip
	env['VMGW']        = gw
	env['VMMASK']      = netmask
	env['VMNS']        = ns
	env['VMDM']        = domain
	env['VMHOST']      = host
	env['NETWORKUUID'] = network
	env['TMPLUUID']    = template
	env['VMIP6']       = ip6
	env['VMGW6']       = gw6
	env['VMMASK6']     = netmask6
	env['SSHKEY']      = sshkey

	subprocess.Popen(os.path.dirname(os.path.dirname(__file__)) + '/gridomatic/deploy.sh', env=env)


def vm_create(request):
	session = create_session()
	form = VMCreateForm(request.POST or None)

	form.fields['network'].choices  = get_network_list(session)
	form.fields['template'].choices = get_template_list(session)
	form.fields['host'].choices     = get_host_list(session)

	if form.is_valid():
		deploy(
			name     = form.cleaned_data['hostname'],
			ip       = form.cleaned_data['ip_address'],
			gw       = form.cleaned_data['gateway'],
			netmask  = form.cleaned_data['netmask'],
			ns       = form.cleaned_data['dns'],
			network  = form.cleaned_data['network'],
			template = form.cleaned_data['template'],
			host     = form.cleaned_data['host'],
			ip6      = form.cleaned_data['ip_address6'],
			gw6      = form.cleaned_data['gateway6'],
			netmask6 = form.cleaned_data['netmask6'],
			sshkey   = form.cleaned_data['sshkey'],
		)
		return redirect('vm_list')
	return render(request, 'gridomatic/vm_create.html', {'form': form})

def network_list(request):
	session = create_session()
	network_list = get_network_list(session)
	return render(request, 'gridomatic/network_list.html', {'networks': network_list})

def network_create(request):
	pass
