from rest_framework.views import APIView,Response
from rest_framework.generics import GenericAPIView
from .models import Test
from rest_framework import status
from.serializers import TestSerializers

class TestDynamicObject(APIView):
    serializer_class = TestSerializers
    def get(self, request, format=None):
        customized_test = Test( 
            msg = "new updated testing data"
        )
        # customized_test.save()
        test = Test.objects.all().values() 
        test = list(test)
        serialized_data = TestSerializers(data=test,many = True)
        serialized_data.is_valid(raise_exception=True)
        return Response(serialized_data.validated_data,status=status.HTTP_201_CREATED)
    
    def post(self, request, format=None):
        serialized_data = TestSerializers(data=request.data)
        serialized_data.is_valid(raise_exception=True) 
        serialized_data.save()
        return Response(serialized_data.validated_data,status=status.HTTP_201_CREATED)