from django import forms
from datetime import datetime

class MessageForm(forms.Form):
    message_text = forms.CharField(label="Enter Message", max_length=1000,
                                   widget=forms.Textarea(attrs={"class": "form-control",
                                                                "placeholder": "Enter message to send to all club "
                                                                               "members"}))


class ClubForm(forms.Form):
    club_name = forms.CharField(label="Enter your club's name", max_length=50,
                                widget=forms.TextInput(attrs={"placeholder": "Enter your club name here",
                                                              "class": "form-control"}))

    description = forms.CharField(label='Enter a little description about your club here', max_length=2000,
                                  widget=forms.Textarea(attrs={"class": "form-control",
                                                               "placeholder": "Enter a description about your club"}))

    public = forms.BooleanField(label="Make your club public?",
                                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}), required=False)


class TimeForm(forms.Form):
    HOURS = [(f'{i:02d}', f'{i:02d}') for i in range(1, 13)]
    DAY_NIGHT = [("AM", "AM"), ("PM", "PM")]

    ## TIMES ##

    ## START TIME ##
    start_hour = forms.ChoiceField(label="Enter the start time of your event", choices=HOURS,
                                   widget=forms.Select(attrs={"class": "form-control"}, choices=HOURS))



    start_day_night = forms.ChoiceField(label="AM or PM?", choices=DAY_NIGHT,
                                        widget=forms.Select(attrs={"class": "form-control"}, choices=DAY_NIGHT))

    ## END TIME ##
    end_hour = forms.ChoiceField(label="Enter the end time of your event", choices=HOURS,
                                 widget=forms.Select(attrs={"class": "form-control"}, choices=HOURS))



    end_day_night = forms.ChoiceField(label="AM or PM?", choices=DAY_NIGHT,
                                      widget=forms.Select(attrs={"class": "form-control"}, choices=DAY_NIGHT))


class When2MeetForm(TimeForm):
    event_name = forms.CharField(label="Enter the title of your event", max_length=50,
                                 widget=forms.TextInput(attrs={"placeholder": "Enter your event name here",
                                                               "class": "form-control"}))

    # date = forms.DateField(label="Enter the date of your event",
    #                        widget=forms.DateInput(attrs={"class": "form-control",
    #                                                      "placeholder": "YYYY-MM-DD"}))


class EventForm(TimeForm):
    MINUTES = [(f'{i:02d}', f'{i:02d}') for i in range(0, 60, 15)]
    event_name = forms.CharField(label="Enter the title of your event", max_length=50,
                                 widget=forms.TextInput(attrs={"placeholder": "Enter your event name here",
                                                               "class": "form-control"}))

    description = forms.CharField(label="Enter a description about your event", max_length=2000,
                                  widget=forms.Textarea(attrs={"class": "form-control",
                                                               "placeholder": "Enter a description about your event"}))

    date = forms.DateField(label="Enter the date of your event",
                           widget=forms.DateInput(attrs={"class": "form-control",
                                                         "placeholder": "YYYY-MM-DD",
                                                         'type': 'date'}))

    location = forms.CharField(label="Enter the location of your event", max_length=100,
                               widget=forms.TextInput(attrs={"class": "form-control",
                                                             "placeholder": "Enter the location of your event"}))
    
    room_number = forms.CharField(label="Room Number/Name", max_length=10,
                                  widget=forms.TextInput(attrs={"class": "form-control",
                                                                "placeholder": "Room Number/Name"}))

    start_minute = forms.ChoiceField(label="Enter the start time of your event", choices=MINUTES,
                                     widget=forms.Select(attrs={"class": "form-control"}, choices=MINUTES))

    end_minute = forms.ChoiceField(label="Enter the start hour of your event", choices=MINUTES,
                                   widget=forms.Select(attrs={"class": "form-control"}, choices=MINUTES))
    
    def clean_date(self):
        if datetime.strptime(self.data['date'], '%Y-%m-%d').date() < datetime.today().date():
            raise forms.ValidationError("Date cannot be in the past")
        return self.data['date']

    def clean_start_hour(self):
        if datetime.strptime(self.data['date'], '%Y-%m-%d').date() == datetime.today().date():
            if datetime.strptime(f"{self.data['start_hour']}-{self.data['start_minute']}-{self.data['start_day_night']}", "%I-%M-%p").time() < datetime.now().time():
                raise forms.ValidationError("Start time cannot be in the past")
        return self.data['start_hour']
    
    def clean_end_hour(self):
        if datetime.strptime(f"{self.data['end_hour']}-{self.data['end_minute']}-{self.data['end_day_night']}", "%I-%M-%p") < \
            datetime.strptime(f"{self.data['start_hour']}-{self.data['start_minute']}-{self.data['start_day_night']}", "%I-%M-%p"):
            raise forms.ValidationError("End time cannot be before start time")
        return self.data['end_hour']
    
    
