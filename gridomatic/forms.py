from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class VMCreateForm(forms.Form):
	hostname     = forms.CharField(label="Hostname" )
	domain       = forms.CharField(label="Domain" )
	description  = forms.CharField(help_text="Please provide a detailed description")

	template     = forms.ChoiceField(choices = [])

	# Memory has to be in KB
	MEMORY_CHOICES = (
		('268435456', '256 MB'),
		('536870912', '512 MB'),
		('1073741824', '1 GB'),
		('2147483648', '2 GB'),
		('4294967296', '4 GB'),
		('6442450944', '6 GB'),
		('8589934592', '8 GB'),
		('10737418240', '10 GB'),
		('12884901888', '12 GB'),
		('15032385536', '14 GB'),
		('17179869184', '16 GB'),
	)

	CPU_CHOICES = (
		('1', '1'),
		('2', '2'),
		('4', '4'),
		('6', '6'),
		('8', '8'),
		('10', '10'),
		('12', '12'),
		('14', '14'),
		('16', '16'),
	)
	mem_size     = forms.ChoiceField(choices = MEMORY_CHOICES, initial='512',label="Memory Size")
	cpu_cores    = forms.ChoiceField(choices = CPU_CHOICES, initial='1', label="CPU Cores", help_text="<br />")

	network      = forms.ChoiceField(choices = [])
	ip_address   = forms.GenericIPAddressField(protocol='ipv4', label="IPv4 Address") 
	ip_address6  = forms.GenericIPAddressField(protocol='ipv6', required=False, label="IPv6 Address (optional)")

	host         = forms.ChoiceField(choices = [])
	backup       = forms.BooleanField(label="Create Backups using XenBackup", required=False, help_text="Check to enable a daily backup of this VM")

	password     = forms.CharField(help_text="Save the password! It will not be shown again!")
	sshkey       = forms.CharField(help_text="Public Key in OpenSSH format", label="SSH key")

	puppet       = forms.BooleanField(label="Enable Puppet", required=False)
	puppetmaster = forms.ChoiceField(choices = [], required=False, help_text="Will only be used if enabled")

	tags        = forms.MultipleChoiceField(choices = [])

	def __init__(self, *args, **kwargs):
		extra = kwargs.pop('extra')
		super(VMCreateForm, self).__init__(*args, **kwargs)

		for key,value in extra.items():
			self.fields['customfield.%s' % key] = forms.CharField(label=key, initial=value)


class NetworkCreateForm(forms.Form):
	name          = forms.CharField(help_text="Name for the new Network")
	description   = forms.CharField(help_text="Please provide a detailed description")
	vlan          = forms.IntegerField(label="VLAN")
	ipv4_gateway  = forms.GenericIPAddressField(protocol='ipv4', label="IPv4 Gateway") 
	ipv4_netmask  = forms.GenericIPAddressField(protocol='ipv4', label="IPv4 netmask") 
	ipv6_gateway  = forms.GenericIPAddressField(protocol='ipv6', required=False, label="IPv6 gateway (Optional)")
	ipv6_netmask  = forms.IntegerField(label='IPv6 netmask (Optional)', required=False, min_value=1, max_value=128)
	dns_servers   = forms.CharField(help_text="Space seperated DNS servers")


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
