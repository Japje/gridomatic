from django.conf import settings
import XenAPI
import sh

class Xen():
	def __init__(self, poolname):
		try:
			session = XenAPI.Session(settings.XENPOOLS[poolname]['url'])
			session.xenapi.login_with_password(settings.XENPOOLS[poolname]['user'], settings.XENPOOLS[poolname]['password'])
		except Exception, e:
			if e.details[0] == 'HOST_IS_SLAVE':
				# Redirect to cluster master
				url = urlparse(url).scheme + '://' + e.details[1]
				session = XenAPI.Session(url)
				session.login_with_password(settings.XENPOOLS[poolname]['user'], settings.XENPOOLS[poolname]['password'])
			else:
				raise Exception(e)
		self.session = session

	def network_list(self):
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


	def network_details(self, uuid):
		network_ref = self.session.xenapi.network.get_by_uuid(uuid)
		network_details = self.session.xenapi.network.get_record(network_ref)
		return network_details


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

	def vmnames_by_vif(self, vifs):
		names = []
		for vif_ref in vifs:
			vm_ref = self.session.xenapi.VIF.get_VM(vif_ref)
			vm_records = self.session.xenapi.VM.get_record(vm_ref)
			if not vm_records["is_a_template"]: 
				names += [{
					'name': vm_records["name_label"],
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
		# Before destroying the VM, first destroy all the Disks and network interfaces the VM has.
		vm_ref = self.session.xenapi.VM.get_by_uuid(uuid)
		vm_details = self.session.xenapi.VM.get_record(vm_ref)
		vbds = vm_details['VBDs']
		vifs = vm_details['VIFs']

		# Loop through all the VBDs
		for vbd_ref in vbds:
			# Each VDB contains a VDI and also has to be destroyed
			vbd_records = self.session.xenapi.VBD.get_record(vbd_ref)
			vdi_ref = self.session.xenapi.VBD.get_VDI(vbd_ref)
			try:
				self.session.xenapi.VDI.destroy(vdi_ref)
			except:
				pass

			try:
				self.session.xenapi.VBD.destroy(vbd_ref)
			except:
				pass

		# Loop through all the VIFs
		for vif_ref in vifs:
			try:
				self.session.xenapi.VIF.destroy(vif_ref)
			except:
				pass
		try:
			self.session.xenapi.VM.destroy(vm_ref)
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
		name           = options['hostname']
		hostname       = options['hostname']
		(name, domain) = name.split('.', 1)

		# Get the host -> PBD -> SR on which we will copy the template
		host_ref = self.session.xenapi.host.get_by_name_label(options['host'])
		pbd_ref  = self.session.xenapi.host.get_PBDs(host_ref[0])

		for ref in pbd_ref:
			config =  self.session.xenapi.PBD.get_device_config(ref)

			if not 'device' in config: continue
			sr_ref = self.session.xenapi.PBD.get_SR(ref)			

		# Get the template Ref and use it to copy to a new VM and set it to be not a VM
		template_ref = self.session.xenapi.VM.get_by_uuid(options['template'])
		vm_ref       = self.session.xenapi.VM.copy(template_ref, str(hostname), sr_ref)

		self.session.xenapi.VM.set_is_a_template(vm_ref, False)

		# TODO create and attach VIF
		network        = options['network'],
		#vif-create vm-uuid=${VMUUID} network-uuid=$NETWORKUUID mac=random device=0
		#self.session.xenapi.VIF.create(records)

		# Let the puppetmaster generate a cert keys for the client, this is safer then having autosign enabled on the puppetmaster
		puppet = self.puppet_gen_certs(hostname)

		# Data to go into xenstore_data
		data = {}
		data['vm-data/ip']     = str(options['ip_address'])
		data['vm-data/gw']     = str(options['gateway'])
		data['vm-data/nm']     = str(options['netmask'])
		data['vm-data/ns']     = str(options['dns'])
		data['vm-data/dm']     = str(domain)
		data['vm-data/sshkey'] = str(options['sshkey'])

		# Optional data
		if options['ip_address6']:
			data['vm-data/ip6'] = str(options['ip_address6'])

		if options['gateway6']:
			data['vm-data/gw6'] = str(options['gateway6'])

		if options['netmask6']:
			data['vm-data/nm6'] = str(options['netmask6'])

		if puppet['pub_cert']:
			data['vm-data/puppet/pub'] = str(puppet['pub_cert'])

		if puppet['prv_cert']:
			data['vm-data/puppet/prv'] = str(puppet['prv_cert'])

		# set the xenstore_data for the vm with above data
		self.session.xenapi.VM.set_xenstore_data(vm_ref, data)
		
		# Update the CPU and Mem. Template stores CPU and Mem but we want to overwrite this with the values from the form
		self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(options['cpu_cores']))
		self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(options['cpu_cores']))
		
		# Set the mem to int, calc to bytes, then back to str.. thanks again citrix for being consistent!
		intmem = int(options['mem_size'])*1024*1024
		mem    = str(intmem)
		self.session.xenapi.VM.set_memory_limits(vm_ref, mem, mem, mem, mem)

		# Set backup flag in customfield
		if options['backup'] is True:
			backup_value = '1'
		else:
			backup_value = '0'
	
		self.session.xenapi.VM.add_to_other_config(vm_ref, 'XenCenter.CustomFields.backup', backup_value)

		self.session.xenapi.VM.set_name_description(vm_ref, str(options['description']))

		# Set PV args		
		self.session.xenapi.VM.set_PV_args(vm_ref, '-- console=hvc')

		# Start the VM
		self.session.xenapi.VM.start(vm_ref, False, True)


	def vm_update(self, uuid, fields):
		memory        = int(fields['mem_size'])*1024*1024
		cpu_cores     = int(fields['cpu_cores'])
		description   = fields['description']
		vm_ref        = self.session.xenapi.VM.get_by_uuid(uuid)
		cur_cpu_cores = int(self.session.xenapi.VM.get_VCPUs_max(vm_ref))

		other_data = {}
		if fields['backup'] is True:
			other_data['XenCenter.CustomFields.backup'] = '1'
		else:
			other_data['XenCenter.CustomFields.backup'] = '0'
	
		self.session.xenapi.VM.set_other_config(vm_ref, other_data)
		


		if cur_cpu_cores >= cpu_cores:
			self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))
			self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
		else:
			self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
			self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))
	
		self.session.xenapi.VM.set_memory_limits(vm_ref, str(memory), str(memory), str(memory),str(memory))

		self.session.xenapi.VM.set_name_description(vm_ref, description)


	def network_update(self, uuid, fields):
		network_ref = self.session.xenapi.network.get_by_uuid(uuid)

		self.session.xenapi.network.set_name_description(network_ref, fields['description'])
		self.session.xenapi.network.set_name_label(network_ref, fields['name'])

		data = {}
		data['racktables_id'] = fields['racktables_id']
		data['automatic']     = 'false'
		self.session.xenapi.network.set_other_config(network_ref, data)

        def disks_by_vdb(self, vbds):
		data = []
		for vbd_ref in vbds:
			vbd_records = self.session.xenapi.VBD.get_record(vbd_ref)
			if not vbd_records['type'] == 'Disk': continue
			vdi_records = self.session.xenapi.VDI.get_record(vbd_records['VDI'])
			data += [{
				'name':                 vdi_records["name_label"],
				'size':                 vdi_records["virtual_size"],
				'physical_utilisation': vdi_records["physical_utilisation"],
			}]
		return data

	def puppet_gen_certs(self, hostname):
		puppetmasterhost = settings.PUPPETMASTER_HOST
		puppetmaster     = sh.ssh.bake("root@"+puppetmasterhost)
		puppetmaster("puppetca --generate "+str(hostname))

		pub  = puppetmaster("base64 -w0 /var/lib/puppet/ssl/ca/signed/"+str(hostname)+".pem")
		prv  = puppetmaster("base64 -w0 /var/lib/puppet/ssl/private_keys/"+str(hostname)+".pem")

		data = {}
		data['pub_cert'] = pub
		data['prv_cert'] = prv
		return data

