from rest_framework import serializers
from .models import Test,TestAbs,TestEmbed

class TestSerializers(serializers.ModelSerializer):
    class Meta:
        model = Test
        read_only_fields = ('_id',)
        fields ="__all__"
        

class TestAbsSerializers(serializers.Serializer):
    desc = serializers.CharField(required=False, allow_null=True)
    desc1 = serializers.CharField(required=False, allow_null=True)

class TestEmbedSerializers(serializers.ModelSerializer):
    test_embed = TestAbsSerializers()
    class Meta:
        model = TestEmbed
        read_only_fields = ('_id',)
        fields ="__all__"