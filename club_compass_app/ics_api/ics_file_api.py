import pytz
from ics import Calendar, Event
from datetime import datetime
import uuid


def get_datetime_str(event_date: str, event_time: str) -> str:
    orig = datetime(*map(int, event_date.split("-")), *map(int, event_time.split(":")))
    eastern = pytz.timezone("US/Eastern")
    gmt_time = eastern.localize(orig).astimezone(pytz.utc)
    return gmt_time.strftime("%Y-%m-%d %H:%M:%S")


def generate_ics(clubs) -> str:
    output_filename = f"{uuid.uuid4()}.ics"
    cal = Calendar()
    for club in clubs:
        for event in club.get_upcoming_events():
            ics_event = Event()
            ics_event.name = event.name
            ics_event.begin = get_datetime_str(str(event.date), str(event.start_time))
            ics_event.end = get_datetime_str(str(event.date), str(event.end_time))
            ics_event.location = event.location
            ics_event.description = event.description
            cal.events.add(ics_event)

    with open(output_filename, 'w') as f:
        f.writelines(cal.serialize_iter())

    return output_filename
