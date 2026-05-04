from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from travel.models import ProjectPlace, TravelProject


class TravelApiHttpCodesTests(TestCase):
    """Covers expected HTTP status codes: 200, 201, 204, 400, 404, 409."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass-secret',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_api_requires_authentication_401(self):
        anon = APIClient()
        r = anon.get('/api/v1/travel/')
        self.assertEqual(r.status_code, 401)

    def test_schema_and_docs_200(self):
        anon = APIClient()
        r = anon.get('/api/schema/')
        self.assertEqual(r.status_code, 200)
        r2 = anon.get('/api/docs/')
        self.assertEqual(r2.status_code, 200)

    def test_create_project_201(self):
        r = self.client.post(
            '/api/v1/travel/',
            {'name': 'Paris trip', 'description': '', 'start_date': None},
            format='json',
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['name'], 'Paris trip')

    def test_list_and_retrieve_project_200(self):
        p = TravelProject.objects.create(name='X')
        r = self.client.get('/api/v1/travel/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)
        r2 = self.client.get(f'/api/v1/travel/{p.pk}/')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data['name'], 'X')

    def test_project_not_found_404(self):
        r = self.client.get('/api/v1/travel/999999/')
        self.assertEqual(r.status_code, 404)

    @patch('travel.serializers.ArticService')
    def test_add_place_201_mock_artic(self, MockArtic):
        mock = MockArtic.return_value
        mock.get_artwork.return_value = {'id': 4, 'title': 'Test artwork'}
        mock.validate_artwork.return_value = True

        p = TravelProject.objects.create(name='T')
        r = self.client.post(
            f'/api/v1/travel/{p.pk}/places/',
            {'external_id': '4', 'notes': '', 'visited': False},
            format='json',
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['title'], 'Test artwork')
        mock.get_artwork.assert_called()

    @patch('travel.serializers.ArticService')
    def test_eleventh_place_400(self, MockArtic):
        mock = MockArtic.return_value
        mock.get_artwork.side_effect = lambda eid: {
            'id': int(eid),
            'title': f'Art {eid}',
        }
        mock.validate_artwork.return_value = True

        p = TravelProject.objects.create(name='Full')
        for i in range(1, 11):
            r = self.client.post(
                f'/api/v1/travel/{p.pk}/places/',
                {'external_id': str(i)},
                format='json',
            )
            self.assertEqual(r.status_code, 201, msg=f'place {i}')

        r11 = self.client.post(
            f'/api/v1/travel/{p.pk}/places/',
            {'external_id': '99'},
            format='json',
        )
        self.assertEqual(r11.status_code, 400)

    @patch('travel.serializers.ArticService')
    def test_delete_project_with_visited_400(self, MockArtic):
        mock = MockArtic.return_value
        mock.get_artwork.return_value = {'id': 7, 'title': 'Vis'}
        mock.validate_artwork.return_value = True

        p = TravelProject.objects.create(name='V')
        self.client.post(
            f'/api/v1/travel/{p.pk}/places/',
            {'external_id': '7'},
            format='json',
        )
        place = ProjectPlace.objects.get(project=p)
        self.client.patch(
            f'/api/v1/travel/{p.pk}/places/{place.pk}/',
            {'visited': True, 'notes': ''},
            format='json',
        )

        r = self.client.delete(f'/api/v1/travel/{p.pk}/')
        self.assertEqual(r.status_code, 400)

    def test_delete_empty_project_204(self):
        p = TravelProject.objects.create(name='Del')
        r = self.client.delete(f'/api/v1/travel/{p.pk}/')
        self.assertEqual(r.status_code, 204)
        self.assertFalse(TravelProject.objects.filter(pk=p.pk).exists())

    @patch('travel.serializers.ArticService')
    def test_duplicate_place_409(self, MockArtic):
        mock = MockArtic.return_value
        mock.get_artwork.return_value = {'id': 100, 'title': 'Dup'}
        mock.validate_artwork.return_value = True

        p = TravelProject.objects.create(name='D')
        r1 = self.client.post(
            f'/api/v1/travel/{p.pk}/places/',
            {'external_id': '100'},
            format='json',
        )
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.post(
            f'/api/v1/travel/{p.pk}/places/',
            {'external_id': '100'},
            format='json',
        )
        self.assertEqual(r2.status_code, 409)

    def test_place_not_found_404(self):
        p = TravelProject.objects.create(name='P')
        r = self.client.get(f'/api/v1/travel/{p.pk}/places/99999/')
        self.assertEqual(r.status_code, 404)
