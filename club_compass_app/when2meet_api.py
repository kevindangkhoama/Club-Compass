import re
from typing import List

import requests


def get_when2meet_link(event_name: str, dates: List[str], start_hour: int, end_hour: int):
    url = "https://www.when2meet.com/SaveNewEvent.php"
    data = {
        "NewEventName": event_name,
        "DateTypes": "SpecificDates",
        "PossibleDates": "|".join(dates),
        "NoEarlierThan": str(start_hour),
        "NoLaterThan": str(end_hour),
        "TimeZone": "America/New_York"
    }
    response = requests.post(url, data=data)

    text = response.content.decode("utf-8")
    pattern = r'body onload="window\.location=\'/?(.*?)\''  # (.*?) captures any character (non-greedy)
    match = re.search(pattern, text)

    if match:
        extracted_text = match.group(1)
        return f"https://www.when2meet.com/{extracted_text}"
    else:
        raise ValueError("When2Meet link not found")
