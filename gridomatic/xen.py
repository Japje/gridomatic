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
		details = self.session.xenapi.VM.get_record(vm_ref)
		#detail_list = []
		#for ref, field in details.items():
		#	print ref
		#	#print field
		#	detail_list += [{
		#		# I have no idea what im doing
		#	}]
		return details
	
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
	
	def vm_restart(self, uuid):
		ref = self.session.xenapi.VM.get_by_uuid(uuid)
		try:
			self.session.xenapi.VM.clean_shutdown(ref)
			self.session.xenapi.VM.start(ref, False, True)
		except:
			pass
	
	def vm_deploy(self, options):
		pass
