from __future__ import annotations
from django.db import models
from autoslug import AutoSlugField
from datetime import date
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Club(models.Model):
    name = models.CharField(max_length=100)
    owner = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    description = models.TextField()
    members = models.ManyToManyField('auth.User', through='Membership', related_name='memberships')
    messages = models.ManyToManyField("Message", related_name="messages")
    events = models.ManyToOneRel('Event', to='Event', field_name='events', related_name='events')
    tags = models.ManyToManyRel('Tag', to='Tag', related_name='tags')
    public = models.BooleanField(default=True)
    slug = AutoSlugField(unique_with='id', populate_from='name')  # Displays name in URL

    # Returns true if the user owns a club else False
    @staticmethod
    def check_user_owns_club(user: User):
        return Club.objects.filter(owner=user).exists()

    @staticmethod
    def get_club_by_owner(user: User):
        return Club.objects.filter(owner=user).first()

    @staticmethod
    def get_public_clubs():
        return Club.objects.filter(public=True)

    # Returns the URL associated with the club
    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"slug": self.slug})

    def get_members(self):
        return self.members.filter(membership__role='member')

    def get_pending_members(self):
        return self.members.filter(membership__role='pending')

    def get_rejected_members(self):
        return self.members.filter(membership__role='rejected')

    def get_events(self):
        return self.events.all()
    
    def get_upcoming_events(self):
        return Event.objects.filter(club=self, date__gte=date.today()).order_by('date', 'start_time')

    def get_desc(self):
        return self.description

    def get_name(self):
        return self.name

    def get_messages(self):
        return self.messages.all().order_by('time_sent')

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=100)

    @staticmethod
    def validate_tag(tag):
        if len(tag) == 0:
            return False
        elif Tag.objects.filter(tag=tag).exists():
            return False
        elif tag.split() > 1:  # contains no spaces
            return False
        return True

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='pending')

    @staticmethod
    def get_users_clubs(user: User):
        return Club.objects.filter(membership__user=user, membership__role='member')

    @staticmethod
    def get_users_pending_clubs(user: User):
        return Club.objects.filter(membership__user=user, membership__role='pending')

    @staticmethod
    def get_users_rejected_clubs(user: User):
        return Club.objects.filter(membership__user=user, membership__role='rejected')

    @staticmethod
    def is_user_account(user: User):
        return Membership.objects.filter(user=user).exists()

    def approve(self):
        self.role = 'member'

    def reject(self):
        self.role = 'rejected'

    def __str__(self):
        return self.user.username + ' is ' + self.role + ' of ' + self.club.name


class RSVP(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    rsvp = models.BooleanField(default=False)

    @staticmethod
    def get_rsvps_for_club(club: Club):
        return RSVP.objects.filter(event__club=club)

    @staticmethod
    def get_rsvps_for_event(event: Event):
        return RSVP.objects.filter(event=event)

    @staticmethod
    def get_rsvps_for_user(user: User):
        return RSVP.objects.filter(user=user)

    def __str__(self):
        return self.user.username + ' is ' + self.rsvp + ' for ' + self.event.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    start_time = models.TimeField()      # TimeField for start time
    end_time = models.TimeField()        # TimeField for end time
    date = models.DateField(default=date.today)            # DateField for date
    location = models.CharField(max_length=100, default="Default Location")
    room_number = models.CharField(max_length=10, default="Lobby")
    tags = models.ManyToManyRel(Tag, to='Tag', related_name='tags')
    rsvp_req = models.BooleanField(default=False)
    rsvps = models.ManyToManyField('auth.User', through='RSVP', related_name='rsvps')

    def __str__(self):
        return self.name


class Message(models.Model):
    text = models.CharField(max_length=1000)
    time_sent = models.DateTimeField(auto_now_add=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    has_link = models.BooleanField(default=False)
    when2meet_link = models.CharField(max_length=200, default="")
