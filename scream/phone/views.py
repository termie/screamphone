import base64
import logging
import random
import urllib
import uuid

from django import http
from django import template
from django import shortcuts
from django.conf import settings
from django.template import loader

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import db

from scream import models


def _ensure_auth(request):
  username = settings.TWILIO_USER
  password = settings.TWILIO_PASSWORD

  basic_auth = request.META.get('HTTP_AUTHORIZATION')
  if not basic_auth:
    return http.HttpResponseForbidden()

  try:
    user_pass = base64.decodestring(basic_auth[6:])
    check_username, check_password = user_pass.split(':')
  except Exception as e:
    return http.HttpResponseServerError(str(e))

  if check_username != username or check_password != password:
    return http.HttpResponseForbidden()


def index(request):
  return shortcuts.render_to_response('templates/index.html', locals())


def twilio_auto(request):
  if 'Digits' in request.POST:
    digits = request.POST['Digits']
    if int(digits) == 1:
      return twilio_scream(request)
    elif int(digits) == 2:
      return twilio_record_scream(request)

  return shortcuts.render(request,
                          'templates/auto.xml',
                          locals(),
                          content_type='text/xml')


def twilio_hangup(request):
  return shortcuts.render(request,
                          'templates/hangup.xml',
                          locals(),
                          content_type='text/xml')


def twilio_scream(request):
  scream = random.choice(list(models.Scream.all()))
  scream_path = scream.url
  return shortcuts.render(request,
                          'templates/scream.xml',
                          locals(),
                          content_type='text/xml')


def twilio_sms(request):
  if 'From' in request.POST:
    logging.info('SMS (%s): %s', request.POST['From'], request.POST.get('Body'))
    from_ = request.POST['From']

    _make_call(from_, 'http://screamphone.appspot.com/twilio/scream')
    return shortcuts.render(request,
                            'templates/empty.xml',
                            locals(),
                            content_type='text/xml')

  return twilio_scream(request)


def _make_call(to, callback):
  logging.info('Calling %s', to)
  url = ('https://api.twilio.com/2010-04-01/Accounts/%s/Calls.xml'
         % settings.TWILIO_ACCOUNT)
  payload = urllib.urlencode({'From': '+14157994205',
                              'Url': callback,
                              'To': to})
  #logging.warn('pay %s', payload)
  creds = '%s:%s' % (settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
  headers = {"Authorization": "Basic %s" % base64.b64encode(creds)}
  result = urlfetch.fetch(url, method=urlfetch.POST, payload=payload, headers=headers)
  #logging.warn('result: %s %s', result.status_code, result.content)
  return result


def twilio_record_scream(request):
  if 'RecordingUrl' in request.POST:
    id = uuid.uuid4().hex
    url = request.POST.get('RecordingUrl')
    duration = request.POST.get('RecordingDuration')

    new_scream = models.Scream(key_name=id,
                               id=id,
                               url=url,
                               duration=int(duration))
    new_scream.save()
    return shortcuts.render(request,
                            'templates/recorded_scream.xml',
                            locals(),
                            content_type='text/xml')


  return shortcuts.render(request,
                          'templates/record_scream.xml',
                          locals(),
                          content_type='text/xml')


