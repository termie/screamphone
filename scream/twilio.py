import base64
import hmac
import logging
from hashlib import sha1


# From the twilio python library: https://github.com/twilio/twilio-python/
class RequestValidator(object):
    def __init__(self, token):
        self.token = token

    def compute_signature(self, uri, params):
        """Compute the signature for a given request

        :param uri: full URI that Twilio requested on your server
        :param params: post vars that Twilio sent with the request
        :param auth: tuple with (account_sid, token)

        :returns: The computed signature
        """
        s = unicode(uri)
        if len(params) > 0:
            for k, v in sorted(params.items()):
                s += k + v

        #logging.info('string %s', s)
        # compute signature and compare signatures
        mac = hmac.new(self.token, s.encode("utf-8"), sha1)
        computed = base64.b64encode(mac.digest())

        #logging.info('computed %s', computed)
        return computed.strip()

    def validate(self, uri, params, signature):
        """Validate a request from Twilio

        :param uri: full URI that Twilio requested on your server
        :param params: post vars that Twilio sent with the request
        :param signature: expexcted signature in HTTP X-Twilio-Signature header
        :param auth: tuple with (account_sid, token)

        :returns: True if the request passes validation, False if not
        """
        #logging.info('validate: %s %s', uri, signature)
        #logging.info('params: %s', params)
        return self.compute_signature(uri, params) == signature
