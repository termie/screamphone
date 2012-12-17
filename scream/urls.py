from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'scream.phone.views.index'),
    (r'^twilio/auto$', 'scream.phone.views.twilio_auto'),
    (r'^twilio/scream$', 'scream.phone.views.twilio_scream'),
    (r'^twilio/sms$', 'scream.phone.views.twilio_sms'),
    (r'^twilio/record/scream$', 'scream.phone.views.twilio_record_scream'),
    #(r'^_ah/warmup$', 'scream.phone.views.warmup'),
    # Example:
    # (r'^scream/', include('scream.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
