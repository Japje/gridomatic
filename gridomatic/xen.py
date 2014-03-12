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
		try:
			networks = self.session.xenapi.network.get_all_records()
		except:
			pass
		return networks


	def network_create(self, options):
		name         = options['name']
		description  = options['description']
		vlan         = str(options['vlan']) # str? yes... str :( TY citrix for being so consistent!
		other_config = {
			'automatic': 'false',
		}
		tags = [ 'Production']

		ipv4_network = str(options['ipv4_gateway'])+'|'+str(options['ipv4_netmask'])
		other_config['XenCenter.CustomFields.network.ipv4'] = ipv4_network

		if  options['ipv6_gateway'] and options['ipv6_netmask']:
			ipv6_network = str(options['ipv6_gateway'])+'|'+str(options['ipv6_netmask'])
			other_config['XenCenter.CustomFields.network.ipv6'] = ipv6_network


		network_ref = self.session.xenapi.network.create({'name_label': name, 'name_description': description, 'other_config': other_config, 'tags': tags})
		self.session.xenapi.pool.create_VLAN('bond0', network_ref, vlan)
		return True


	def network_details_uuid(self, uuid):
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
		try:
			vms = self.session.xenapi.VM.get_all_records()
		except:
			pass
		return vms


	def vm_details(self, uuid):
		vm_ref = self.session.xenapi.VM.get_by_uuid(uuid)
		vm_details = self.session.xenapi.VM.get_record(vm_ref)
		return vm_details

	def get_tags(self):
		poolrefs = self.session.xenapi.pool.get_all()
		tags = self.session.xenapi.pool.get_tags(poolrefs[0])
		return tags

	def get_other_config(self):
		poolrefs = self.session.xenapi.pool.get_all()
		other_config = self.session.xenapi.pool.get_other_config(poolrefs[0])
		return other_config

	def network_details_ref(self, vifs):
		names = []
		for vif_ref in vifs:
			net_ref = self.session.xenapi.VIF.get_network(vif_ref)
			net = self.session.xenapi.network.get_record(net_ref)
			names += [{
				'name':        net['name_label'],
				'uuid':        net['uuid'],
			}]
		return names

	def vmdetails_by_vif(self, vifs):
		names = []
		for vif_ref in vifs:
			vm_ref = self.session.xenapi.VIF.get_VM(vif_ref)
			vm_records = self.session.xenapi.VM.get_record(vm_ref)
			if not vm_records["is_a_template"]: 
				names += [{
					'name': vm_records["name_label"],
					'uuid': vm_records["uuid"],
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
		name     = options['hostname']
		domain   = options['domain']
		hostname = name+'.'+domain

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
		network_ref  = self.session.xenapi.network.get_by_uuid(options['network'])

		template_vif = self.session.xenapi.VM.get_VIFs(vm_ref)

		for vif in template_vif:
			self.session.xenapi.VIF.destroy(vif)

		vif_config   = { 
			'device': '0',
			'network': network_ref,
			'VM': vm_ref,
			'MAC': '',
			'MTU': '1500',
			'qos_algorithm_type': '',
			'qos_algorithm_params': {},
			'other_config': {} 
		}

		try:
			self.session.xenapi.VIF.create(vif_config)
		except Exception, e:
			raise Exception(e)

		tags = options['tags']

		self.session.xenapi.VM.set_tags(vm_ref, tags)

		vm_details = self.session.xenapi.VM.get_record(vm_ref)
		vbds = vm_details['VBDs']
		for vbd_ref in vbds:
			# Each VDB contains a VDI
			vbd_records = self.session.xenapi.VBD.get_record(vbd_ref)
			if vbd_records['type'] == 'Disk':
				vdi_ref = self.session.xenapi.VBD.get_VDI(vbd_ref)
				self.session.xenapi.VDI.set_name_label(vdi_ref, hostname+' root')
				self.session.xenapi.VDI.set_name_description(vdi_ref, 'Created by the Grid-o-Matic deployment tool')

		# Let the puppetmaster generate a cert keys for the client, this is safer then having autosign enabled on the puppetmaster
		if options['puppet'] is True:
			puppet = self.puppet_gen_certs(options['puppetmaster'],hostname)

		network_ref  = self.session.xenapi.network.get_by_uuid(options['network'])
		network_other_config = self.session.xenapi.network.get_other_config(network_ref)

		# Data to go into xenstore_data
		data = {}
		data['vm-data/ip']       = str(options['ip_address'])

		data['vm-data/gw']       = str(network_other_config['XenCenter.CustomFields.network.ipv4']).split('|', 2)[0]
		data['vm-data/nm']       = str(network_other_config['XenCenter.CustomFields.network.ipv4']).split('|', 2)[1]
		data['vm-data/ns']       = str(network_other_config['XenCenter.CustomFields.network.dns'])

		data['vm-data/hostname'] = str(options['hostname'])
		data['vm-data/domain']  = str(options['domain'])
		data['vm-data/sshkey']   = str(options['sshkey'])
		data['vm-data/password'] = str(options['password'])

		# Optional data
		if options['ip_address6']:
			data['vm-data/ip6'] = str(options['ip_address6'])
			# gateway and netmask are pulled from the customfields of the network
			if 'XenCenter.CustomFields.network.ipv6' in network_other_config:
				data['vm-data/gw6'] = str(network_other_config['XenCenter.CustomFields.network.ipv6']).split('|', 2)[0]
				data['vm-data/nm6'] = str(network_other_config['XenCenter.CustomFields.network.ipv6']).split('|', 2)[1]
			else:
				data['vm-data/gw6'] = ""
				data['vm-data/nm6'] = ""

		if options['puppet'] is True:
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
		mem    = str(options['mem_size'])

		self.session.xenapi.VM.set_memory_limits(vm_ref, mem, mem, mem, mem)

		other_data = {}

		# Set backup flag in customfield
		if options['backup'] is True:
			other_data['XenCenter.CustomFields.backup'] = '1'
		else:
			other_data['XenCenter.CustomFields.backup'] = '0'

		for item in options:
			if 'customfield' not in item: continue
			field = str(item.split('.')[1])
			other_data['XenCenter.CustomFields.%s' % field] = str(options[item])

		self.session.xenapi.VM.set_other_config(vm_ref, other_data)

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

		tags          = fields['tags']

		self.session.xenapi.VM.set_tags(vm_ref, tags)

		other_data = {}
		if fields['backup'] is True:
			other_data['XenCenter.CustomFields.backup'] = '1'
		else:
			other_data['XenCenter.CustomFields.backup'] = '0'

		for item in fields:
			if 'customfield' not in item: continue
			field = str(item.split('.')[1])
			other_data['XenCenter.CustomFields.%s' % field] = str(fields[item])

		self.session.xenapi.VM.set_other_config(vm_ref, other_data)
		self.session.xenapi.VM.set_name_description(vm_ref, description)

		vm_details = self.session.xenapi.VM.get_record(vm_ref)

		if vm_details['power_state'] == 'Halted':

			if cur_cpu_cores >= cpu_cores:
				self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))
				self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
			else:
				self.session.xenapi.VM.set_VCPUs_max(vm_ref, str(cpu_cores))
				self.session.xenapi.VM.set_VCPUs_at_startup(vm_ref, str(cpu_cores))

			self.session.xenapi.VM.set_memory_limits(vm_ref, str(memory), str(memory), str(memory),str(memory))


	def network_update(self, uuid, fields):
		network_ref = self.session.xenapi.network.get_by_uuid(uuid)

		self.session.xenapi.network.set_name_description(network_ref, fields['description'])
		self.session.xenapi.network.set_name_label(network_ref, fields['name'])

		data = {}
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

	def puppet_gen_certs(self, puppetmasterhost,hostname):
		puppetmaster     = sh.ssh.bake("root@"+puppetmasterhost)
		puppetmaster("puppetca --generate "+str(hostname))

		pub  = puppetmaster("base64 -w0 /var/lib/puppet/ssl/ca/signed/"+str(hostname)+".pem")
		prv  = puppetmaster("base64 -w0 /var/lib/puppet/ssl/private_keys/"+str(hostname)+".pem")

		data = {}
		data['pub_cert'] = pub
		data['prv_cert'] = prv
		return data


	def host_details(self, host_ref):
		host_details = self.session.xenapi.host.get_record(host_ref)
		return host_details
