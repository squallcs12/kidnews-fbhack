from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication

from accountkit.models import Account


class TokenAuthentication(BaseTokenAuthentication):
    model = Account
