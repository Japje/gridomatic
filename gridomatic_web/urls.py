from django.conf.urls import patterns, include, url

from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
	url(r'^', include('gridomatic.urls')),
	url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('djcelery.views',
	url(r'^ajax/task/status/(?P<task_id>.+)/$', 'task_status', name='task-status')
)