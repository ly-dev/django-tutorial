from django.contrib.auth.models import User, Group
from rest_framework import serializers

class GroupSerializer(serializers.Serializer):
    url = serializers.URLField()
    name = serializers.CharField(max_length=100)


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
