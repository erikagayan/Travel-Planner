from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from travel.views import ProjectPlaceViewSet, TravelProjectViewSet

router = DefaultRouter()
router.register(r'travel', TravelProjectViewSet, basename='travelproject')

places_router = NestedDefaultRouter(router, r'travel', lookup='project')
places_router.register(r'places', ProjectPlaceViewSet, basename='project-places')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(places_router.urls)),
]
