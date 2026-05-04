from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from travel.models import ProjectPlace, TravelProject
from travel.services import ArticService


class TravelProjectSerializer(serializers.ModelSerializer):
    places_count = serializers.SerializerMethodField()

    class Meta:
        model = TravelProject
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'status',
            'created_at',
            'places_count',
        )
        read_only_fields = ('id', 'status', 'created_at', 'places_count')

    def get_places_count(self, obj):
        if hasattr(obj, 'places_count'):
            return obj.places_count
        return obj.places.count()


class TravelProjectCreateSerializer(serializers.ModelSerializer):
    place_ids = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = TravelProject
        fields = ('name', 'description', 'start_date', 'place_ids')

    def validate(self, attrs):
        raw_ids = attrs.get('place_ids') or []
        cleaned = []
        seen = set()
        for pid in raw_ids:
            s = str(pid).strip()
            if not s:
                raise ValidationError({'place_ids': 'Place ids must be non-empty.'})
            if s in seen:
                raise ValidationError({'place_ids': f'Duplicate place id: {s}'})
            seen.add(s)
            cleaned.append(s)

        if len(cleaned) > 10:
            raise ValidationError({'place_ids': 'Maximum 10 places per project.'})

        artic = ArticService()
        for ext_id in cleaned:
            if not artic.validate_artwork(ext_id):
                raise ValidationError(
                    {'place_ids': f'Artwork {ext_id} not found in Art Institute API.'}
                )

        attrs['place_ids'] = cleaned
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        place_ids = validated_data.pop('place_ids', [])
        project = TravelProject.objects.create(**validated_data)
        artic = ArticService()
        for ext_id in place_ids:
            data = artic.get_artwork(ext_id)
            eid = str(data.get('id', ext_id))
            title = (data.get('title') or '')[:512]
            ProjectPlace.objects.create(
                project=project,
                external_id=eid,
                title=title,
            )
        return project


class ProjectPlaceSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(write_only=True, max_length=64)

    class Meta:
        model = ProjectPlace
        fields = (
            'id',
            'project',
            'external_id',
            'title',
            'notes',
            'visited',
            'added_at',
        )
        read_only_fields = ('id', 'title', 'added_at')

    @transaction.atomic
    def create(self, validated_data):
        external_id = str(validated_data.pop('external_id')).strip()
        artic = ArticService()
        data = artic.get_artwork(external_id)
        if not data:
            raise ValidationError({'external_id': 'Not found in Art Institute API.'})
        validated_data['external_id'] = str(data.get('id', external_id))
        validated_data['title'] = (data.get('title') or '')[:512]
        return ProjectPlace.objects.create(**validated_data)


class ProjectPlaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = ('notes', 'visited')
