from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

class VMCreateForm(forms.Form):
	hostname     = forms.CharField(label="FDQN Hostname")
	description  = forms.CharField(help_text="Please provide a detailed description")

	ip_address   = forms.GenericIPAddressField(protocol='ipv4', label="IP Address") 
	netmask      = forms.GenericIPAddressField(protocol='ipv4')
	gateway      = forms.GenericIPAddressField(protocol='ipv4')
	dns          = forms.CharField(help_text="List of space seperated Nameserver Addresses", label="DNS Servers")

	ip_address6  = forms.GenericIPAddressField(protocol='ipv6', required=False, label="IPv6 Address")
	netmask6     = forms.IntegerField(label='IPv6 Prefixlength', required=False, min_value=1, initial=64, max_value=128)
	gateway6     = forms.GenericIPAddressField(protocol='ipv6', required=False, label='IPv6 Gateway', )


	template     = forms.ChoiceField(choices = [])
	network      = forms.ChoiceField(choices = [])
	host         = forms.ChoiceField(choices = [])

	mem_size     = forms.IntegerField(label="Memory Size (MB)", min_value=256, initial=256)
	cpu_cores    = forms.IntegerField(label="CPU Cores", initial=1, min_value=1)

	password     = forms.CharField(help_text="Copy this password! It will NOT be shown again!")
	sshkey       = forms.CharField(help_text="Public Key in OpenSSH format", label="SSH key")

	backup       = forms.BooleanField(label="Create Backups using XenBackup", required=False)
	puppet       = forms.BooleanField(label="Enable Puppet", required=False)
	puppetmaster = forms.ChoiceField(choices = [], required=False, help_text="Will only be used if enabled")
	tags        = forms.MultipleChoiceField(choices = [])

	def __init__(self, *args, **kwargs):
		extra = kwargs.pop('extra')
		super(VMCreateForm, self).__init__(*args, **kwargs)

		for key,value in extra.items():
			self.fields['customfield.%s' % key] = forms.CharField(label=key, initial=value)


class NetworkCreateForm(forms.Form):
	name        = forms.CharField(help_text="Name for the new Network")
	description = forms.CharField(help_text="Please provide a detailed description")
	vlan        = forms.IntegerField(label="VLAN")

class VMEditForm(forms.Form):
	description = forms.CharField(help_text="Please provide a detailed description", label="Description")
	mem_size    = forms.IntegerField(label="Memory Size", help_text="Size in MB (Only editable if VM is Halted)", min_value=256)
	cpu_cores   = forms.IntegerField(label="CPU Cores", help_text="(Only editable if VM is Halted)", initial=1, min_value=1)
	backup      = forms.BooleanField(help_text="Select if we should create Backups for this VM", label="Create Backups", required=False)
	tags        = forms.MultipleChoiceField(choices = [])

	def __init__(self, *args, **kwargs):
		extra = kwargs.pop('extra')
		super(VMEditForm, self).__init__(*args, **kwargs)

		for key,value in extra.items():
			self.fields['customfield.%s' % key] = forms.CharField(label=key, initial=value)

class NetworkEditForm(forms.Form):
	name          = forms.CharField(help_text="Please provide a name")
	description   = forms.CharField(help_text="Please provide a detailed description")

class TagsForm(forms.Form):
	tags = forms.MultipleChoiceField(choices = [])
