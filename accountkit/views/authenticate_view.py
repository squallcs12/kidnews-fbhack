import hashlib
import hmac

import requests
from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accountkit.models import Account
from accountkit.serializers.account_serializer import AccountSerializer
from accounts.models import User


class AccountKitException(APIException):
    default_detail = "AccountKit fail to work."
    status_code = 400

    def __init__(self, resp, *args, **kwargs):
        self.resp = resp
        super(AccountKitException, self).__init__(*args, **kwargs)
        self.status_code = resp.status_code


class AuthenticateView(APIView):
    permission_classes = (AllowAny,)

    me_endpoint_base_url = 'https://graph.accountkit.com/{}/me'.format(settings.ACCOUNT_KIT_API_VERSION)
    token_exchange_base_url = 'https://graph.accountkit.com/{}/access_token'.format(settings.ACCOUNT_KIT_API_VERSION)

    def post(self, request):
        """
        Facebook account kit authenticate
        @param request:
        @return:
        ---
        response_serializer: accountkit.serializers.account_serializer.AccountSerializer
        parameters:
            - name: code
              required: true
        """
        """
        function loadLoginSuccess() {
  return fs.readFileSync('dist/login_success.html').toString();
}

app.post('/sendcode', function(request, response){
  console.log('code: ' + request.body.code);

  // CSRF check
  if (request.body.csrf_nonce === csrf_guid) {
    var app_access_token = ['AA', app_id, app_secret].join('|');
    """
        app_access_token = '|'.join(['AA', settings.AUTH_FACEBOOK_KEY, settings.ACCOUNT_KIT_APP_SECRET])

        """
    var params = {
      grant_type: 'authorization_code',
      code: request.body.code,
      access_token: app_access_token
    };"""
        params = {
            'grant_type': 'authorization_code',
            'code': request.data['code'],
            'access_token': app_access_token,
        }
        """

    // exchange tokens
    var token_exchange_url = token_exchange_base_url + '?' + Querystring.stringify(params);
    Request.get({url: token_exchange_url, json: true}, function(err, resp, respBody) {
    """
        response = requests.get(self.token_exchange_base_url, params=params)
        if response.status_code >= 400:
            raise AccountKitException(response)
        token_data = response.json()

        """
      var view = {
        user_access_token: respBody.access_token,
        expires_at: respBody.expires_at,
        user_id: respBody.id,
      };
      // get account details at /me endpoint
      var me_endpoint_url = me_endpoint_base_url + '?access_token=' + respBody.access_token;
      Request.get({url: me_endpoint_url, json:true }, function(err, resp, respBody) {
      """
        access_token = token_data['access_token']
        appsecret_proof = hmac.new(
            settings.ACCOUNT_KIT_APP_SECRET.encode('utf-8'),
            access_token.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        response = requests.get(self.me_endpoint_base_url, {
            'access_token': access_token,
            'appsecret_proof': appsecret_proof,
        })
        me_data = response.json()
        try:
            account = Account.objects.get(account_id=me_data['id'])
        except Account.DoesNotExist:
            user = User.objects.create()
            account = Account.objects.create(account_id=me_data['id'],
                                             user=user,
                                             data=me_data)
        return Response(AccountSerializer(account).data)
        """
        // send login_success.html
        if (respBody.phone) {
          view.phone_num = respBody.phone.number;
        } else if (respBody.email) {
          view.email_addr = respBody.email.address;
        }
        var html = Mustache.to_html(loadLoginSuccess(), view);
        response.send(html);
      });
    });
  }
  else {
    // login failed
    response.writeHead(200, {'Content-Type': 'text/html'});
    response.end("Something went wrong. :( ");
  }
});
        @param request:
        @return:
        """
