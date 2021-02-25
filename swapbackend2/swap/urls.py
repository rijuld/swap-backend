# myapi/urls.py
from django.urls import include, path
from rest_framework import routers
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from . import views

router = routers.DefaultRouter()
router.register(r'courses', views.CoursesViewSet)
router.register(r'users', views.NewUserViewSet)
router.register(r'require', views.RequireViewSet)
router.register(r'authtok', views.authtokViewSet)
router.register(r'devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]