from rest_framework import serializers

from accountkit.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'user', 'account_id', 'data', 'key')
