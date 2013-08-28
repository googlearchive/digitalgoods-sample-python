# Copyright 2013 Google Inc. All Rights Reserved.                                            

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable-msg=C6409,C6203

"""In-App Payments - Online Store Python Sample"""

# standard library imports
from cgi import escape
import os
import time

# third-party imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import jwt

# application-specific imports
from sellerinfo import SELLER_ID
from sellerinfo import SELLER_SECRET

class MainHandler(webapp.RequestHandler):
  """Handles /"""

  def get(self):
    """Handles get requests."""

    curr_time = int(time.time())
    exp_time = curr_time + 3600

    request_info = {'currencyCode': 'USD',
                    'sellerData': 'Custom Data'}
    jwt_info = {'iss': SELLER_ID,
                'aud': 'Google',
                'typ': 'google/payments/inapp/item/v1',
                'iat': curr_time,
                'exp': exp_time,
                'request': request_info}

    # create JWT for first item
    request_info.update({'name': 'Drive In Aniversary Poster', 'price': '20.00'})
    token_1 = jwt.encode(jwt_info, SELLER_SECRET)

    # create JWT for second item
    request_info.update({'name': 'Golden Gate Bridge Poster', 'price': '25.00'})
    token_2 = jwt.encode(jwt_info, SELLER_SECRET)

    # update store web page
    template_vals = {'jwt_1': token_1,
                     'jwt_2': token_2}

    path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    self.response.out.write(template.render(path, template_vals))


class PostbackHandler(webapp.RequestHandler):
  """Handles server postback - received at /postback"""

  def post(self):
    """Handles post request."""
    encoded_jwt = self.request.get('jwt', None)
    if encoded_jwt is not None:
      # jwt.decode won't accept unicode, cast to str
      # http://github.com/progrium/pyjwt/issues/4
      decoded_jwt = jwt.decode(str(encoded_jwt), SELLER_SECRET)

      # validate the payment request and respond back to Google
      if decoded_jwt['iss'] == 'Google' and decoded_jwt['aud'] == SELLER_ID:
        if ('response' in decoded_jwt and
            'orderId' in decoded_jwt['response'] and
            'request' in decoded_jwt):
          order_id = decoded_jwt['response']['orderId']
          request_info = decoded_jwt['request']
          if ('currencyCode' in request_info and 'sellerData' in request_info
              and 'name' in request_info and 'price' in request_info):
            # optional - update local database
            
            # respond back to complete payment
            self.response.out.write(order_id)


application = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/postback', PostbackHandler),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
