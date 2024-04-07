from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from club_compass import settings


urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.Home.as_view(), name='home'), # home page for users to see their clubs
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('create_club/', views.Login.as_view(), name='club_login'),
    path('clubs/<slug:slug>/send_message', views.SendMessage.as_view(), name='send_message'),
    path('clubs/add_event', views.AddEvent.as_view(), name='add_event'),
    path('clubs/send_when2meet', views.SendWhen2Meet.as_view(), name='send_when2meet'),
    path('clubs/', views.Discover.as_view(), name="discover"),
    path('clubs/<slug:slug>/join', views.join_club, name='join_club'),
    path('clubs/<slug:slug>/', views.ClubDetail.as_view(), name='club_detail'),
    path('clubs/<slug:slug>/user', views.UserClubDetail.as_view(), name='user_club_detail'),
    path('clubs/<slug:slug>/approve/<int:user_pk>', views.approve_member, name='approve_member'),
    path('clubs/<slug:slug>/reject/<int:user_pk>', views.reject_member, name='reject_member'),
    path('download_calendar', views.download_calendar, name="download_calendar"),
    path('login_confirmation', views.login_confirmation, name="login_confirmation"),
    # Calls a provided logout method to log the user out and returns to the home screen
    # The LOGOUT_REDIRECT_URL is set in club_compass/settings.py at the bottom
]
