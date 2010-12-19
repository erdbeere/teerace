from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('race.views',
	url(r'^activity/$', 'user_activity', name='user_activity'),
	url(r'^maps/$', 'map_list', name='maps'),
	url(r'^maps/(?P<map_id>\d+)/$', 'map_detail', name='map_detail'),
	url(r'^ranks/$', 'ranks', name='ranks'),
	url(r'^ranks/maps/$', 'ranks_map_list', name='ranks_map_list'),
	url(r'^ranks/maps/(?P<map_id>\d+)/$', 'ranks_map_detail', name='ranks_map_detail'),
)