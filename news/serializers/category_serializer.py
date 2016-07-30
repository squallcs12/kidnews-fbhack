from rest_framework import serializers

from news.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Model:
        model = Category
        fields = ('id', 'name')
