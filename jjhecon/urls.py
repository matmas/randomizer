from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jjhecon.views.home', name='home'),
    # url(r'^jjhecon/', include('jjhecon.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    (r'^r/?$', 'jjhecon.randomizer.views.json_view'), # deprecate this
    (r'^r/.json/?$', 'jjhecon.randomizer.views.json_view'),
    (r'^r/.html/?$', 'jjhecon.randomizer.views.html_view'),
    (r'^r/(\w+)/?$', 'jjhecon.randomizer.views.visit'),
    (r'^r/a/(\w+)/?$', 'jjhecon.randomizer.views.admin'),
    (r'^wait/?$', 'jjhecon.scheduler.views.wait'),
    (r'^schedule/?$', 'jjhecon.scheduler.views.schedule'),
    (r'^sandbox/?$', 'jjhecon.randomizer.views.sandbox'),
    (r'^s/mturk_iframe/?$', 'jjhecon.scheduler.views.mturk_iframe'),
)
