from django_filters import rest_framework as filters

from travel.models import ProjectPlace, TravelProject


class TravelProjectFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=TravelProject.Status.choices)

    class Meta:
        model = TravelProject
        fields = ['status']


class ProjectPlaceFilter(filters.FilterSet):
    visited = filters.BooleanFilter()

    class Meta:
        model = ProjectPlace
        fields = ['visited']
