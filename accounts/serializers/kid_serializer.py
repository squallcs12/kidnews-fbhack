from rest_framework import serializers

from accounts.models import Kid


class KidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kid
        fields = ('id', 'user', 'name', 'birthyear', 'picture')
        read_only_fields = ('user', )
