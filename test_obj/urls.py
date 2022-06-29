from .views import TestDynamicObject

from django.urls import path

urlpatterns = [
    path('test',TestDynamicObject.as_view(),name = "test")
]