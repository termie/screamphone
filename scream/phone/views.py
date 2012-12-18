import base64
import functools
import logging
import os
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
from scream import twilio


def _ensure_auth(f):
  @functools.wraps(f)
  def _wrap(request):
    if request.META.get('SERVER_SOFTWARE', '').startswith('Development'):
      return f(request)

    validator = twilio.RequestValidator(settings.TWILIO_TOKEN)
    url = request.build_absolute_uri()
    sig = request.META['HTTP_X_TWILIO_SIGNATURE']
    if not validator.validate(url, request.POST, sig):
      return http.HttpResponseForbidden()

    return f(request)
  return _wrap


def _make_sms(to, body):
  logging.info('SMSing %s', to)
  url = ('https://api.twilio.com/2010-04-01/Accounts/%s/SMS/Messages.xml'
         % settings.TWILIO_ACCOUNT)
  payload = urllib.urlencode({'From': '+14157994205',
                              'To': to,
                              'Body': body})
  #logging.warn('pay %s', payload)
  creds = '%s:%s' % (settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
  headers = {"Authorization": "Basic %s" % base64.b64encode(creds)}
  result = urlfetch.fetch(url,
                          method=urlfetch.POST,
                          payload=payload,
                          headers=headers)
  #logging.warn('result: %s %s', result.status_code, result.content)
  return result


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


def index(request):
  return shortcuts.render_to_response('templates/index.html', locals())


@_ensure_auth
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


@_ensure_auth
def twilio_hangup(request):
  return shortcuts.render(request,
                          'templates/hangup.xml',
                          locals(),
                          content_type='text/xml')


@_ensure_auth
def twilio_scream(request):
  all_screams = list(models.Scream.all())
  if not all_screams:
    all_screams = ['/sounds/scream_3.mpg']
  scream = random.choice(all_screams)
  # If it has a url attrib use it, else assume it is a string
  scream_path = getattr(scream, 'url', scream)
  return shortcuts.render(request,
                          'templates/scream.xml',
                          locals(),
                          content_type='text/xml')


@_ensure_auth
def twilio_sms(request):
  if 'From' in request.POST:
    #logging.info('SMS (%s): %s', from_, body)
    from_ = request.POST['From']
    body = request.POST['Body']
    logging.info('SMS (%s): %s', from_, body)

    if body == 'test_foo':
      _make_sms(from_, 'test_foo')
      return shortcuts.render(request,
                              'templates/empty.xml',
                              locals(),
                              content_type='text/xml')

    _make_call(from_, 'http://screamphone.appspot.com/twilio/scream')
    return shortcuts.render(request,
                            'templates/empty.xml',
                            locals(),
                            content_type='text/xml')

  return twilio_scream(request)


@_ensure_auth
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


