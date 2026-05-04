from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from travel.filters import ProjectPlaceFilter, TravelProjectFilter
from travel.models import ProjectPlace, TravelProject
from travel.serializers import (
    ProjectPlaceSerializer,
    ProjectPlaceUpdateSerializer,
    TravelProjectCreateSerializer,
    TravelProjectSerializer,
)


class TravelProjectViewSet(viewsets.ModelViewSet):
    queryset = TravelProject.objects.annotate(
        places_count=Count('places', distinct=True),
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TravelProjectFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return TravelProjectCreateSerializer
        return TravelProjectSerializer

    def perform_destroy(self, instance):
        if instance.places.filter(visited=True).exists():
            raise ValidationError(
                'Cannot delete a project that has visited places.',
            )
        super().perform_destroy(instance)


class ProjectPlaceViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectPlaceFilter

    def get_queryset(self):
        return ProjectPlace.objects.filter(project_id=self.kwargs['project_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        pk = self.kwargs.get('project_pk')
        if pk is not None:
            context['project_pk'] = pk
        return context

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return ProjectPlaceUpdateSerializer
        return ProjectPlaceSerializer

    def perform_create(self, serializer):
        project = get_object_or_404(TravelProject, pk=self.kwargs['project_pk'])
        try:
            serializer.save(project=project)
        except IntegrityError:
            raise ValidationError(
                'This artwork is already in the project.',
            ) from None
