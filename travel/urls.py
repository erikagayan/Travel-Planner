from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from travel.views import ProjectPlaceViewSet, TravelProjectViewSet

router = DefaultRouter()
router.register(r'projects', TravelProjectViewSet, basename='travelproject')

projects_router = NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'places', ProjectPlaceViewSet, basename='project-places')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(projects_router.urls)),
]
