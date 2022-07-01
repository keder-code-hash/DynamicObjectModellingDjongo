from rest_framework import serializers
from .models import Test,TestAbs,TestEmbed

class TestSerializers(serializers.ModelSerializer):
    class Meta:
        model = Test
        read_only_fields = ('_id',)
        fields ="__all__"
        

class TestAbsSerializers(serializers.Serializer):
    desc = serializers.CharField(required=False, allow_null=True,allow_blank = True)
    desc1 = serializers.CharField(required=False, allow_null=True,allow_blank = True)
    desc2 = serializers.CharField(required=False, allow_null=True,allow_blank = True)

    # file_testing_fields = serializers.FileField()

    created_at = serializers.DateTimeField(read_only = True)
    updated_at = serializers.DateTimeField(read_only = True)

    created_at_date = serializers.DateField(read_only = True)
    updated_at_date = serializers.DateField(read_only = True)
    
    created_at_time = serializers.TimeField(read_only = True)
    updated_at_time = serializers.TimeField(read_only = True)



class TestEmbedSerializers(serializers.ModelSerializer):
    test_embed = TestAbsSerializers(required = False)
    class Meta:
        model = TestEmbed
        read_only_fields = ('_id',)
        fields ="__all__"