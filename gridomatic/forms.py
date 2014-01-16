from django import forms

class VMCreateForm(forms.Form):
	hostname   = forms.CharField()

	ip_address  = forms.GenericIPAddressField(protocol='ipv4', label="IP Address") 
	netmask     = forms.GenericIPAddressField(protocol='ipv4')
	gateway     = forms.GenericIPAddressField(protocol='ipv4')
	dns         = forms.CharField(help_text="List of space seperated Nameserver Adresses", label="DNS Servers")

	ip_address6 = forms.GenericIPAddressField(protocol='ipv6', label="IPv6 Address", required=False) 
	netmask6    = forms.CharField(help_text="Subnet number like 64", required=False)
	gateway6    = forms.GenericIPAddressField(protocol='ipv6', required=False)


	template    = forms.ChoiceField(choices = [])
	network     = forms.ChoiceField(choices = [])
	host        = forms.ChoiceField(choices = [])

	disk_size   = forms.IntegerField(help_text="Size in GB")
	mem_size    = forms.IntegerField(help_text="Size in MB")
	cpu_cores   = forms.IntegerField()

	sshkey      = forms.CharField(help_text="Your PUBLIC ssh-key", label="SSH-key")

class NetworkCreateForm(forms.Form):
	name        = forms.CharField(help_text="Name for the new Network", label="Name")
	description	= forms.CharField(help_text="Please provide a detailed description!", label="Description")
	vlan			= forms.IntegerField()
