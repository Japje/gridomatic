from django.conf import settings
import XenAPI

class Xen():
	def __init__(self):
		try:
			session = XenAPI.Session(settings.XEN_URL)
			session.xenapi.login_with_password(settings.XEN_USER, settings.XEN_PASSWORD)
		except Exception, e:
			if e.details[0] == 'HOST_IS_SLAVE':
				# Redirect to cluster master
				url = urlparse(url).scheme + '://' + e.details[1]
				session = XenAPI.Session(url)
				session.login_with_password(settings.XEN_USER, settings.XEN_PASSWORD)
			else:
				raise Exception(e)
		self.session = session

	def get_network_list(self):
		networks = self.session.xenapi.network.get_all_records()
		network_list = []
		for net in networks:
			if not 'Production' in networks[net]['tags']: continue
			network_list += [(networks[net]['uuid'], networks[net]['name_label'])]
		return network_list

	def network_list_dev(self):
		networks = self.session.xenapi.network.get_all_records()
		network_list = []
		for ref, net in networks.items():
			if not 'Production' in net['tags']: continue
			network_list += [{
				'name':        net['name_label'],
				'description': net['name_description'],
				'uuid':        net['uuid'],
			}]
		return network_list

	def network_create(self, options):
		name         = options['name']
		description  = options['description']
		vlan         = str(options['vlan']) # str? yes... str :( TY citrix for being so consistent!
		other_config = {
			'automatic': 'false',
		}
		tags = [ 'Production']

		network_ref = self.session.xenapi.network.create({'name_label': name, 'name_description': description, 'other_config': other_config, 'tags': tags})
		self.session.xenapi.pool.create_VLAN('bond0', network_ref, vlan)
		return True

	def get_template_list(self):
		templates = self.session.xenapi.VM.get_all_records()
		template_list = []
		for tpl in templates:
			if not 'Production' in templates[tpl]['tags']: continue
			if not templates[tpl]["is_a_template"]: continue
			template_list += [(templates[tpl]['uuid'], templates[tpl]['name_label'])]
		return template_list

	def get_host_list(self):
		hosts = self.session.xenapi.host.get_all_records()
		host_list = []
		for host in hosts:
			host_list += [(hosts[host]['name_label'], hosts[host]['name_label'])]
		return host_list
	
	def vm_list(self):
		vms = self.session.xenapi.VM.get_all_records()
		vm_list = []
		for ref, vm in vms.items():
			if vm["is_a_template"] or vm['is_a_snapshot'] or vm["is_control_domain"]: continue

			vm_list += [{
				'name':        vm['name_label'],
				'power_state': vm['power_state'],
				'uuid':        vm['uuid'],
			}]
		return vm_list


	def vm_details(self, uuid):
		vm_ref = self.session.xenapi.VM.get_by_uuid(uuid)
		vm_details = self.session.xenapi.VM.get_record(vm_ref)
		return vm_details

	def network_names(self, vifs):
		names = []
		for vif_ref in vifs:
			net_ref = self.session.xenapi.VIF.get_network(vif_ref)
			net_name = self.session.xenapi.network.get_name_label(net_ref)
			names += [{
				'name':        net_name,
			}]
		return names

	def vm_start(self, uuid):
		ref = self.session.xenapi.VM.get_by_uuid(uuid)
		try:
			self.session.xenapi.VM.start(ref, False, True)
		except:
			pass
	
	def vm_stop(self, uuid):
		ref = self.session.xenapi.VM.get_by_uuid(uuid)
		try:
			self.session.xenapi.VM.clean_shutdown(ref)
		except:
			pass

	def vm_destroy(self, uuid):
		ref = self.session.xenapi.VM.get_by_uuid(uuid)
		try:
			self.session.xenapi.VM.destroy(ref)
		except:
			pass
	
	def vm_restart(self, uuid):
		ref = self.session.xenapi.VM.get_by_uuid(uuid)
		try:
			self.session.xenapi.VM.clean_shutdown(ref)
			self.session.xenapi.VM.start(ref, False, True)
		except:
			pass
	
	def vm_deploy(self, options):
		name     = options['hostname'],
		hostname     = options['hostname'],
		network  = options['network'],
		sshkey   = options['sshkey'],
		(name, domain) = name[0].split('.', 1)

		host_ref = self.session.xenapi.host.get_by_name_label(options['host'])
		pbd_ref  = self.session.xenapi.host.get_PBDs(host_ref[0])
		for ref in pbd_ref:
			config =  self.session.xenapi.PBD.get_device_config(ref)
                        if not 'device' in config: continue
			sr_ref = self.session.xenapi.PBD.get_SR(ref)			

		template_ref = self.session.xenapi.VM.get_by_uuid(options['template'])
		vm_ref = self.session.xenapi.VM.copy(template_ref, str(hostname[0]), sr_ref)
		self.session.xenapi.VM.set_is_a_template(vm_ref, False)

		# TODO puppet.dostuff()

		# TODO create and attach VIF
		#vif-create vm-uuid=${VMUUID} network-uuid=$NETWORKUUID mac=random device=0
		#self.session.xenapi.VIF.create(records)

		self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/ip '+options['ip_address'])
		self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/gw '+options['gateway'])
		self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/nm '+options['netmask'])
		self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/ns '+options['dns'])
		self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/dm '+options['domain'])

		try:
			self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/ip6 ', options['ip_address6'])
			self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/gw6 ', options['gateway6'])
			self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/nm6 ', options['gateway6'])
		except:
			pass

		# below should be converted to base64 values
		#self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/sshkey', sshkey)
		#self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/puppet/pub', puppet_pup)
		#self.session.xenapi.VM.set_xenstore_data(vm_ref, 'vm-data/puppet/prv', puppet_prv)

		self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(options['cpu_cores']))
		self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(options['cpu_cores']))
		intmem = int(option['memory'])*1024*1024
		mem = str(intmem)
		#self.session.xenapi.VM.set_memory_limits(vm_ref, mem, mem, mem, mem)
		
		self.session.xenapi.VM.set_PV_args(vm_ref, '-- console=hvc')
		self.session.xenapi.VM.start(vm_ref, False, True)

	def vm_update(self, uuid, fields):
		memory = int(fields['mem_size'])*1024*1024
		cpu_cores = int(fields['cpu_cores'])
		description = fields['description']
		vm_ref = self.session.xenapi.VM.get_by_uuid(uuid)
		cur_cpu_cores = int(self.session.xenapi.VM.get_VCPUs_max(vm_ref))

		if cur_cpu_cores >= cpu_cores:
			self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))
			self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
		else:
			self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
			self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))
	
		self.session.xenapi.VM.set_memory_limits(vm_ref, str(memory), str(memory), str(memory),str(memory))
		self.session.xenapi.VM.set_name_description(vm_ref, description)
