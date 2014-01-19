from django import forms

class VMCreateForm(forms.Form):
	hostname    = forms.CharField()

	ip_address  = forms.GenericIPAddressField(protocol='ipv4', label="IP Address") 
	netmask     = forms.GenericIPAddressField(protocol='ipv4')
	gateway     = forms.GenericIPAddressField(protocol='ipv4')
	dns         = forms.CharField(help_text="List of space seperated Nameserver Adresses", label="DNS Servers")

	ip_address6 = forms.GenericIPAddressField(protocol='ipv6', required=False, label="IPv6 Address")
	netmask6    = forms.IntegerField(label='IPv6 Prefixlength', required=False, min_value=1, initial=64, max_value=128)
	gateway6    = forms.GenericIPAddressField(protocol='ipv6', required=False, label='IPv6 Gateway', )


	template    = forms.ChoiceField(choices = [])
	network     = forms.ChoiceField(choices = [])
	host        = forms.ChoiceField(choices = [])

	mem_size    = forms.IntegerField(help_text="Size in MB", min_value=128)
	cpu_cores   = forms.IntegerField(initial=1, min_value=1)

	sshkey      = forms.CharField(help_text="In OpenSSH format", label="SSH Public Key")

class NetworkCreateForm(forms.Form):
	name        = forms.CharField(help_text="Name for the new Network", label="Name")
	description = forms.CharField(help_text="Please provide a detailed description!", label="Description")
	vlan        = forms.IntegerField()


class VMEditForm(forms.Form):
	description	= forms.CharField(help_text="Please provide a detailed description!", label="Description")
	mem_size        = forms.IntegerField(help_text="Size in MB", min_value=128)
	cpu_cores       = forms.IntegerField(initial=1, min_value=1)

class NetworkEditForm(forms.Form):
	name		= forms.CharField(help_text="Please provide a name!", label="name")
	description	= forms.CharField(help_text="Please provide a detailed description!", label="Description")
	racktables_id	= forms.CharField(help_text="network_id from racktables", label="Racktables_id")
