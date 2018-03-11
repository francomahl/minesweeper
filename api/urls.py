from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from api import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'games', views.GameViewSet, base_name='api_games')
router.register(r'users', views.UserViewSet, base_name='api_users')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls))
]