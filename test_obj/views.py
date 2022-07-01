from rest_framework.views import APIView,Response
from rest_framework.generics import GenericAPIView
from .models import Test, TestEmbed
from rest_framework import status
from.serializers import TestSerializers,TestEmbedSerializers
from .models import TestEmbed,TestAbs

class TestDynamicObject(APIView):
    serializer_class = TestEmbedSerializers
    def get(self, request, format=None):

        # customized_test = TestEmbed(test_embed=TestAbs(desc = "hii"))
        # customized_test.save()

        test = TestEmbed.objects.all().values() 
        test = list(test)
        print(test)

        serialized_data = self.serializer_class(data=test,many = True)
        serialized_data.is_valid(raise_exception=True)
        return Response(serialized_data.validated_data,status=status.HTTP_201_CREATED)
    
    def post(self, request, format=None):
        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True) 
        serialized_data.save()
        return Response(serialized_data.validated_data,status=status.HTTP_201_CREATED)