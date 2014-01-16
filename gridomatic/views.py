from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
import XenAPI
from forms import VMCreateForm

def create_session():
        try:
                session = XenAPI.Session(settings.XEN_URL)
                session.xenapi.login_with_password(settings.XEN_USER, settings.XEN_PASSWORD)
        except Exception, e:
                if e.details[0] == 'HOST_IS_SLAVE':
                        # Redirect to cluster master
                        url = urlparse(url).scheme + '://' + e.details[1]
                        try:
                                session = XenAPI.Session(url)
                                session.login_with_password(settings.XEN_USER, settings.XEN_PASSWORD)
                        except Exception, e:
                                handle_login_error(e)
                else:
                        handle_login_error(e)
        return session



def get_network_list(session):
	networks = session.xenapi.network.get_all_records()
	network_list = []
	for net in networks:
		if not 'Production' in networks[net]['tags']: continue
		network_list += [(networks[net]['uuid'], networks[net]['name_label'])]
	return network_list

def get_template_list(session):
	templates = session.xenapi.VM.get_all_records()
	template_list = []
	for tpl in templates:
		if not 'Production' in templates[tpl]['tags']: continue
		if not templates[tpl]["is_a_template"]: continue
		template_list += [(templates[tpl]['uuid'], templates[tpl]['name_label'])]
	return template_list

def get_host_list(session):
	hosts = session.xenapi.host.get_all_records()
	host_list = []
	for host in hosts:
		host_list += [(hosts[host]['name_label'], hosts[host]['name_label'])]
	return host_list

def vm_list(request):
	session = create_session()
	vms = session.xenapi.VM.get_all_records()
	vm_list = []
	for ref, vm in vms.items():
		if vm["is_a_template"] or vm['is_a_snapshot'] or vm["is_control_domain"]: continue

		vm_list += [{
			'name': vm['name_label'],
			'power_state': vm['power_state'],
			'uuid': vm['uuid']
		}]
	return render(request, 'gridomatic/vm_list.html', {'vms': vm_list})

def vm_start(request):
	uuid = request.POST.get('uuid', None)
	if not uuid:
		return redirect('vm_list')
	session = create_session()
	ref = session.xenapi.VM.get_by_uuid(uuid)
	try:
		session.xenapi.VM.start(ref, False, True)
	except:
		pass
	return redirect('vm_list')

def vm_stop(request):
	uuid = request.POST.get('uuid', None)
	if not uuid:
		return redirect('vm_list')
	session = create_session()
	ref = session.xenapi.VM.get_by_uuid(uuid)
	try:
		session.xenapi.VM.clean_shutdown(ref)
	except:
		pass
	return redirect('vm_list')

def vm_restart(request):
	uuid = request.POST.get('uuid', None)
	if not uuid:
		return redirect('vm_list')
	session = create_session()
	ref = session.xenapi.VM.get_by_uuid(uuid)
	try:
		session.xenapi.VM.clean_shutdown(ref)
		session.xenapi.VM.start(ref, False, True)
	except:
		pass
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

