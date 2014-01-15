from django import forms

class VMCreateForm(forms.Form):
	hostname   = forms.CharField()

	ip_address = forms.GenericIPAddressField(protocol='ipv4', label="IP Address") # enable 'both' once jasper implemented ipv6 support for it in the shell script
	netmask    = forms.GenericIPAddressField(protocol='ipv4')
	gateway    = forms.GenericIPAddressField(protocol='ipv4')
	dns        = forms.CharField(help_text="List of space seperated Nameserver Adresses", label="DNS Servers")

	template   = forms.ChoiceField(choices = [])
	network    = forms.ChoiceField(choices = [])
	host       = forms.ChoiceField(choices = [])

	disk_size  = forms.IntegerField(help_text="Size in GB")
	mem_size   = forms.IntegerField(help_text="Size in MB")
	cpu_cores  = forms.IntegerField()
