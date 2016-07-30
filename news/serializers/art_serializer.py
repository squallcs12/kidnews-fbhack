from rest_framework import serializers

from news.models import Art


class ArtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Art
        fields = ('picture',)
