from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
 
register = template.Library()
 
def json2html(val):
	out = ''
	if type(val) == list:
		out += '<ul>'
		for i in val:
			out += '<li>' + json2html(i) + '</li>'
		out += '</ul>'
		return mark_safe(out)
	elif type(val) == dict:
		out += '<ul>'
		for prop in val.keys():
			out += '<li><strong>' + prop + ':</strong> ' + json2html(val[prop]) + '</li>'
		out += '</ul>'
		return mark_safe(out)
	else:
		return conditional_escape(unicode(val))
 
 
register.filter('json2html', json2html)
