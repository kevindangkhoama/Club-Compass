# REFERENCES
# Title: "unittest.mock — mock object library"
# URL: https://docs.python.org/3/library/unittest.mock.html
# Software License: PSF LICENSE AGREEMENT

from django.test import TestCase
from unittest.mock import patch
from .when2meet_api import get_when2meet_link
from django.contrib.auth.models import User
from .models import Club, Membership, Event, Message
from .forms import ClubForm, EventForm, MessageForm, TimeForm, When2MeetForm
from datetime import date
import requests
from django.urls import reverse
from django.conf import settings # Import the settings file to get the Google Maps API key
# Create your tests here.

class GoogleMapsIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.club = Club.objects.create(name='Test Club', owner=self.user, description='Test Club Description')
        self.url = reverse('add_event')

    def test_google_maps_api_usage(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Access the API key from the settings
        api_key = settings.GOOGLE_MAPS_API_KEY
        
        # Modify the URL to include the API key
        api_url = f'https://maps.googleapis.com/maps/api/js?key={api_key}'
        
        # Make the request to the Google Maps API
        api_response = requests.get(api_url)
        
        # Check if the API request was successful (status code 200)
        self.assertEqual(api_response.status_code, 200)

        # Check if the API key is present in the context
        self.assertIn('key', response.context)
        google_maps_api_key = response.context['key']
        self.assertEqual(google_maps_api_key, api_key)


class ClubModelTest(TestCase):
    def setUpTestData(self):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='testpassword')

        # Create a test club
        self.test_club = Club.objects.create(
            name='Test Club',
            owner=test_user,
            description='This is a test club',
            public=True,
        )

        # Create a test event
        self.test_event = Event.objects.create(
            club=self.test_club,
            date=date.today(),
            name='Test Event',
            description='Test event description',
        )

        # Create a test message
        self.test_message = Message.objects.create(
            club=self.test_club,
            sender=test_user,
            content='Test message content',
        )
        

class FormsTestCase(TestCase):
    
    # Test cases for Message Forms 
    def test_message_form_is_valid(self):
        form_data = {
            'message_text': 'test message'
        }
        form = MessageForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_message_form_is_not_valid(self):
        form_data = {}
        form = MessageForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    # Test cases for Club Forms   
    def test_club_form_is_valid(self):
        form_data = {
            'club_name': 'club',
            'description': 'description.'
            'public: True'
        }
        form = ClubForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_club_form_is_not_valid(self):
        form_data = {}
        form = ClubForm(data=form_data)
        self.assertFalse(form.is_valid())

    # Test cases for Time Forms
    def test_time_form_is_valid(self):
        form_data = {
            'start_hour': '01',  
            'start_day_night': 'AM',  
            'start_minute': '00', 
            'end_hour': '02',  
            'end_day_night': 'PM', 
            'end_minute': '30',
        }
        form = TimeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_time_form_is_not_valid(self):
        form_data = {}
        form = TimeForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    # Test cases for When2Meet Forms
    def test_when2meet_form_is_valid(self):
        form_data = {
            'event_name': 'test event',
            'date': '2023-12-31', 
            'start_hour': '01',  
            'start_day_night': 'AM',  
            'start_minute': '00', 
            'end_hour': '02',  
            'end_day_night': 'PM', 
            'end_minute': '30',
        }
        form = When2MeetForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_when2meet_form_is_not_valid(self):
        form_data = {}
        form = When2MeetForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    # Test cases for Event Forms
    def test_event_form_is_valid(self):
        form_data = {
            'event_name': 'test event',
            'description': 'description.',
            'date': '2023-12-31', 
            'location': 'test location',
            'start_hour': '01',  
            'start_day_night': 'AM',  
            'start_minute': '00', 
            'end_hour': '02',  
            'end_day_night': 'PM', 
            'end_minute': '30',
            'room_number': '101',
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_event_form_is_not_valid(self):
        form_data = {}
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())


class MembershipModelTestCase(TestCase):
    def setUp(self):
        # Create a user and a club for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.club = Club.objects.create(owner=self.user, name='Test Club')
    
    def test_membership_creation(self):
        # Create a membership for the user and club
        membership = Membership.objects.create(user=self.user, club=self.club, role='pending')

        # Check that the membership was created with the correct data
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.club, self.club)
        self.assertEqual(membership.role, 'pending')

    def test_membership_approval(self):
        # Create a membership with a 'pending' role
        membership = Membership.objects.create(user=self.user, club=self.club, role='pending')
        membership.approve()

        self.assertEqual(membership.role, 'member')

    def test_membership_string_representation(self):
        # Create a membership
        membership = Membership.objects.create(user=self.user, club=self.club, role='member')

        # Check the string representation of the membership
        expected_str = f'{self.user.username} is member of {self.club.name}'
        self.assertEqual(str(membership), expected_str)

class TestWhen2Meet(TestCase):
    @patch('requests.post')
    def test_get_when2meet_link(self, mock_post):
        # Mock the response from requests.post
        mock_response = mock_post.return_value
        mock_response.content = b'body onload="window.location=\'/Event-1234567890\''

        event_name = "Test Event"
        dates = ["2023-12-31", "2024-01-01"]
        start_hour = 9
        end_hour = 17

        expected_link = "https://www.when2meet.com/Event-1234567890"
        actual_link = get_when2meet_link(event_name, dates, start_hour, end_hour)

        self.assertEqual(expected_link, actual_link)
        
