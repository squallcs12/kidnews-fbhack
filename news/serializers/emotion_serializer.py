from rest_framework import serializers

from news.models import EMOTIONS


class EmotionSerializer(serializers.Serializer):
    emotion = serializers.ChoiceField(write_only=True, choices=EMOTIONS)
    emotions = serializers.DictField(read_only=True)
    user_emotion = serializers.ChoiceField(read_only=True, choices=EMOTIONS)
