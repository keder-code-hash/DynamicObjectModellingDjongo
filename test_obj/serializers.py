from rest_framework import serializers
from .models import Test

class TestSerializers(serializers.ModelSerializer):
    class Meta:
        model = Test
        read_only_fields = ('_id',)
        fields ="__all__"
        