from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Estate


class UpdateLocationCsrfTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='secret123',
            is_staff=True,
        )
        self.estate = Estate.objects.create(
            name='Test Estate',
            location_name='Westlands',
            exact_address='Test address',
            latitude='-1.292100',
            longitude='36.821900',
        )

    def test_staff_can_update_location_with_valid_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        edit_response = client.get(reverse('edit_estate', args=[self.estate.pk]))
        csrf_token = edit_response.cookies['csrftoken'].value

        response = client.post(
            reverse('update_location', args=[self.estate.pk]),
            {'latitude': '1.234567', 'longitude': '2.345678'},
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.estate.refresh_from_db()
        self.assertEqual(str(self.estate.latitude), '1.234567')
        self.assertEqual(str(self.estate.longitude), '2.345678')

    def test_update_location_rejects_missing_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(
            reverse('update_location', args=[self.estate.pk]),
            {'latitude': '1.234567', 'longitude': '2.345678'},
        )

        self.assertEqual(response.status_code, 403)

    @patch('excellence.models.Nominatim')
    def test_set_location_falls_back_to_location_name_when_geocode_fails(self, mock_nominatim):
        mock_nominatim.return_value.geocode.return_value = None

        estate = Estate.objects.create(
            name='Fallback Estate',
            location_name='Westlands',
            exact_address='',
        )

        estate.save()

        self.assertEqual(estate.exact_address, 'Westlands')

    @patch('excellence.models.Nominatim')
    def test_update_address_uses_location_name_when_reverse_geocode_fails(self, mock_nominatim):
        mock_nominatim.return_value.reverse.side_effect = Exception('lookup failed')

        estate = Estate(
            name='Reverse Fallback Estate',
            location_name='Kilimani',
            exact_address='',
            latitude='-1.300000',
            longitude='36.800000',
        )

        estate.update_exact_address_from_coordinates()

        self.assertEqual(estate.exact_address, 'Kilimani')


class PropertiesPaginationTests(TestCase):
    def setUp(self):
        for i in range(5):
            Estate.objects.create(
                name=f'Property {i + 1}',
                location_name='Westlands',
                exact_address=f'Address {i + 1}',
                latitude='-1.292100',
                longitude='36.821900',
            )

    def test_properties_page_paginates_results(self):
        response = self.client.get(reverse('properties'), {'page': 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)
        self.assertEqual(response.context['page_obj'].object_list[0].name, 'Property 4')
        self.assertEqual(response.context['page_obj'].object_list[1].name, 'Property 5')


class HomeSearchFilterTests(TestCase):
    def setUp(self):
        Estate.objects.create(
            name='Westlands Villa',
            location_name='Westlands',
            exact_address='Westlands, Nairobi',
            latitude='-1.292100',
            longitude='36.821900',
        )
        Estate.objects.create(
            name='Kilimani Estate',
            location_name='Kilimani',
            exact_address='Kilimani, Nairobi',
            latitude='-1.300000',
            longitude='36.800000',
        )

    def test_index_search_filters_by_location(self):
        response = self.client.get(reverse('index'), {'location': 'Westlands'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['estates']), 1)
        self.assertEqual(response.context['estates'][0].location_name, 'Westlands')


class GoogleDriveAuthTests(TestCase):
    @patch('excellence.views.Flow.from_client_secrets_file')
    @patch('excellence.views.os.path.exists', return_value=True)
    def test_google_drive_login_redirects_to_authorization_url(self, mock_exists, mock_from_client_secrets):
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ('https://accounts.google.com/o/oauth2/auth', 'state-123')
        mock_from_client_secrets.return_value = mock_flow

        response = self.client.get(reverse('google_drive_login'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['google_state'], 'state-123')
        self.assertEqual(response.url, 'https://accounts.google.com/o/oauth2/auth')
