import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

PARIS_TZ = ZoneInfo("Europe/Paris")

def clean_text(text):
    return str(text).replace(",", "\\,").replace(";", "\\;")

def make_uid(match, index):
    return f"worldcup2026-{index}-{match['date']}-{match['time'].replace(':', '')}@github-calendar"

def format_ics_datetime(dt):
    return dt.strftime("%Y%m%dT%H%M%S")

with open("matches.json", "r", encoding="utf-8") as f:
    matches = json.load(f)

ics_lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//World Cup 2026 Calendar//FR//",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:Matchs 2026",
    "X-WR-TIMEZONE:Europe/Paris"
]

now = datetime.now(PARIS_TZ).strftime("%Y%m%dT%H%M%S")

for index, match in enumerate(matches, start=1):
    start = datetime.fromisoformat(f"{match['date']}T{match['time']}:00").replace(tzinfo=PARIS_TZ)
    end = start + timedelta(hours=2)

    title = f"{match['home_flag']} {match['home']} - {match['away_flag']} {match['away']}"
    location = match.get("stadium", "")

    ics_lines.extend([
        "BEGIN:VEVENT",
        f"UID:{make_uid(match, index)}",
        f"DTSTAMP;TZID=Europe/Paris:{now}",
        f"DTSTART;TZID=Europe/Paris:{format_ics_datetime(start)}",
        f"DTEND;TZID=Europe/Paris:{format_ics_datetime(end)}",
        f"SUMMARY:{clean_text(title)}",
        f"LOCATION:{clean_text(location)}",
        "BEGIN:VALARM",
        "TRIGGER:-PT1H",
        "ACTION:DISPLAY",
        f"DESCRIPTION:Rappel : {clean_text(title)}",
        "END:VALARM",
        "END:VEVENT"
    ])

ics_lines.append("END:VCALENDAR")

with open("worldcup2026.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics_lines))