from rest_framework import serializers
from .models import Url

class UrlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Url
        fields = '__all__'
    owner = serializers.ReadOnlyField(source='owner.session.session_key')
