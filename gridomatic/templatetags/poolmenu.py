from django import template
from django.conf import settings

register = template.Library()

def vm_menu():
	pools = settings.XENPOOLS
	return {'pools': sorted(pools)}

register.inclusion_tag('vm_menu.html')(vm_menu)


def network_menu():
	pools = settings.XENPOOLS
	return {'pools': sorted(pools)}

register.inclusion_tag('network_menu.html')(network_menu)

