import os
from typing import Any
from django.http.response import HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views import generic

from .FileResponseWithCleanup import FileResponseWithCleanup
from .ics_api.ics_file_api import generate_ics
from .models import Club, Membership, Message, Event
from .forms import ClubForm, MessageForm, EventForm, When2MeetForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.conf import settings

from .when2meet_api import get_when2meet_link


# Create your views here.


def login(request):
    if request.user.is_authenticated:
        if Club.check_user_owns_club(request.user):
            return redirect(f"/clubs/{Club.get_club_by_owner(request.user).slug}")
        # If the user is authenticated, redirect them to the home page
        return redirect('/home/')
    return render(request, 'club_compass_app/accountTypeSelectionScreen.html')


def get_24_hour_hour(hour, am_pm):
    hour = int(hour)
    if am_pm == "AM" and hour == 12:
        hour -= 12
    elif am_pm == "PM" and hour != 12:
        hour += 12
    return hour


def get_24_hour_time(hour, minute, am_pm):
    return f"{get_24_hour_hour(hour, am_pm):02d}:{minute}:00"


def send_message(club, message_text):
    message = Message(text=message_text, club=club)
    message.save()
    club.messages.add(message)


def send_linked_message(club, message_text, link):
    message = Message(text=message_text, club=club, has_link=True, when2meet_link=link)
    message.save()
    club.messages.add(message)


def get_start_end_times_from_form(time_form):
    start_hour = time_form.cleaned_data.get('start_hour', 'NA')
    start_minute = time_form.cleaned_data.get('start_minute', 'NA')
    start_day_night = time_form.cleaned_data.get('start_day_night', 'NA')
    start_time = get_24_hour_time(start_hour, start_minute, start_day_night)

    end_hour = time_form.cleaned_data.get('end_hour', 'NA')
    end_minute = time_form.cleaned_data.get('end_minute', 'NA')
    end_day_night = time_form.cleaned_data.get('end_day_night', 'NA')
    end_time = get_24_hour_time(end_hour, end_minute, end_day_night)

    return start_time, end_time


class SendWhen2Meet(UserPassesTestMixin, generic.FormView):
    template_name = "club_compass_app/when2meet.html"
    form_class = When2MeetForm
    success_url = "/"

    def form_valid(self, form):
        if self.request.user.is_authenticated \
                and Club.check_user_owns_club(self.request.user):
            event_name = form.cleaned_data['event_name']
            club = Club.get_club_by_owner(self.request.user)
            dates = self.request.POST.getlist('dates')
            if type(dates) == str:
                dates = [dates]
            start_time, end_time = map(lambda time: int(time[:2]), get_start_end_times_from_form(form))
            when2meet_link = get_when2meet_link(event_name, dates, start_time, end_time)
            send_linked_message(club, f"""A new when2meet link was posted for {event_name}""", when2meet_link)
            return super().form_valid(form)
        else:
            return redirect("/")

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        if Membership.is_user_account(self.request.user):
            return False

        if not Club.check_user_owns_club(self.request.user):
            return False

        return True


class AddEvent(UserPassesTestMixin, generic.FormView):
    template_name = "club_compass_app/add_event.html"
    context = {'key': settings.GOOGLE_MAPS_API_KEY}
    form_class = EventForm
    success_url = "/"
    
    def get_context_data(self, location_query = None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['key'] = settings.GOOGLE_MAPS_API_KEY
        context['location_query'] = location_query if location_query is not None else "UVA" # Default value to set location over UVA
        return context
    
    def query_location(self, location_query):
        print("running")
        location_query = location_query.replace(" ", "+")
        self.get_context_data(location_query)
    
    def form_invalid(self, form):
        print("Form is invalid!")
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print("event request")
        if self.request.user.is_authenticated \
                and Club.check_user_owns_club(self.request.user):
            
            event_name = form.cleaned_data['event_name']
            club = Club.get_club_by_owner(self.request.user)
            description_ = form.cleaned_data['description']
            date = form.cleaned_data['date']

            start_time, end_time = get_start_end_times_from_form(form)
            
            location = form.cleaned_data['location']
            room_number = form.cleaned_data['room_number']
            club = Club.get_club_by_owner(self.request.user)
            event = Event(name=event_name, description=description_, club=club, start_time = start_time, 
              end_time=end_time, date=date, location=location, room_number=room_number)
            event.save()
            return super().form_valid(form)
        else:
            return redirect("/")

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        if Membership.is_user_account(self.request.user):
            return False

        if not Club.check_user_owns_club(self.request.user):
            return False

        return True


class SendMessage(UserPassesTestMixin, generic.FormView):
    template_name = "club_compass_app/send_message.html"
    form_class = MessageForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["club_slug"] = Club.get_club_by_owner(self.request.user).slug
        return context

    def form_valid(self, form):
        print("message request")
        if self.request.user.is_authenticated \
                and Club.check_user_owns_club(self.request.user):
            message_text = form.cleaned_data['message_text']
            club = Club.get_club_by_owner(self.request.user)
            send_message(club, message_text)
            # print(club.messages.all())
            # club_name = form.cleaned_data['club_name']
            # description = form.cleaned_data['description']
            # owner = self.request.user
            # public = form.cleaned_data['public']
            # club = Club(name=club_name, description=description, owner=owner, public=public)
            # club.save()
            return super().form_valid(form)
        else:
            return redirect("/")

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        if Membership.is_user_account(self.request.user):
            return False

        if not Club.check_user_owns_club(self.request.user):
            return False

        return True


class Login(UserPassesTestMixin, generic.FormView):
    template_name = "club_compass_app/create_club.html"
    form_class = ClubForm
    success_url = "/home/"

    def form_valid(self, form):
        if self.request.user.is_authenticated \
                and Club.check_user_owns_club(self.request.user) == 0:

            club_name = form.cleaned_data['club_name']
            description = form.cleaned_data['description']
            owner = self.request.user
            public = form.cleaned_data['public']
            club = Club(name=club_name, description=description, owner=owner, public=public)
            club.save()
            # TODO add tags
            return super().form_valid(form)
        else:
            return redirect("/")

    def handle_no_permission(self) -> HttpResponseRedirect:
        if Membership.is_user_account(self.request.user):
            return redirect('/login_confirmation')
        return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return True
        else:
            return not Club.check_user_owns_club(self.request.user)\
                and not Membership.is_user_account(self.request.user)


def logout_view(request):
    # Calls a built in method to log the user out and returns to the home screen
    if request.method == "POST":
        logout(request)
        return redirect("/")


class Home(UserPassesTestMixin, generic.ListView):
    template_name = 'club_compass_app/home.html'
    context_object_name = 'clubs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_events"] = False

        for c in Membership.get_users_clubs(self.request.user):
            if len(c.get_upcoming_events()) > 0:
                context["has_events"] = True
                break

        return context

    def get_queryset(self):
        return Club.objects.filter(membership__user=self.request.user, membership__role='member')

    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.user.is_authenticated:
            return redirect(f'/login_confirmation')
        else:
            return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if Club.check_user_owns_club(self.request.user):
            return False
        
        return True

class UserClubDetail(UserPassesTestMixin, generic.DetailView):
    login_url = "/"
    model = Club
    template_name = "club_compass_app/user_club_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = self.object.get_name()
        context["description"] = self.object.get_desc()
        context["messages"] = self.object.get_messages()
        context['events'] = self.object.get_upcoming_events()
        context['key'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("/")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        return self.request.user in self.get_object().get_members()


class ClubDetail(UserPassesTestMixin, generic.DetailView):
    login_url = "/"
    model = Club
    template_name = 'club_compass_app/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['memberships'] = self.object.get_members()
        context['pending_members'] = self.object.get_pending_members()
        context['rejected_members'] = self.object.get_rejected_members()
        context['club'] = self.get_object()
        context["club_slug"] = self.object.slug
        return context

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect("/")

    # Checks if the user owns the club
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if not self.get_object().check_user_owns_club(self.request.user):
            return False

        return True

class Discover(UserPassesTestMixin, generic.ListView):
    template_name = 'club_compass_app/discover.html'
    context_object_name = 'clubs'

    def get_queryset(self):  # shows the user clubs that they are not a member of
        return Club.get_public_clubs().filter(~Q(membership__user=self.request.user))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # If they are logged in and they own a club, redirect them to their club
            return redirect(f"/clubs/{Club.get_club_by_owner(self.request.user).slug}")
        else:
            return redirect("/")  # If there not logged in redirect to the login page

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if Club.check_user_owns_club(self.request.user):
            return False
        
        return True

@login_required
def login_confirmation(request):
    if not request.user.is_authenticated:
        return redirect("/")

    return render(request, 'club_compass_app/login_confirmation.html',
                  context={'club_member': Membership.is_user_account(request.user),})

@login_required
def join_club(request, slug):
    if not request.user.is_authenticated:
        return redirect("/")
    
    club = Club.objects.get(slug=slug)
    if club is None:
        return redirect("/")
    
    if club.public is False:
        return redirect("/")

    if Membership.objects.filter(user=request.user, club=club).exists():
        return redirect("/")
    
    Membership(user=request.user, club=club).save()
    return redirect("/home/")


@login_required
def approve_member(request, slug, user_pk):
    if request.user.is_authenticated \
            and Club.objects.get(slug=slug).check_user_owns_club(request.user):
        pending_user = User.objects.get(pk=user_pk)
        membership = Membership.objects.get(user=pending_user, club__slug=slug)
        membership.approve()
        membership.save()
        return redirect(f"/clubs/{slug}")
    
    else:
        return redirect("/")


@login_required
def reject_member(request, slug, user_pk):
    if request.user.is_authenticated \
            and Club.check_user_owns_club(request.user):
        pending_user = User.objects.get(pk=user_pk)
        membership = Membership.objects.get(user=pending_user, club__slug=slug)
        membership.reject()
        membership.save()
        return redirect(f"/clubs/{slug}")
    
    return redirect("/")


@login_required
def download_calendar(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not Membership.is_user_account(request.user):
        return redirect("/")

    clubs = Membership.get_users_clubs(request.user)

    ics_filename = generate_ics(clubs)
    return FileResponseWithCleanup(open(ics_filename, 'rb'), as_attachment=True, filename='club_events.ics', file_path=ics_filename)
