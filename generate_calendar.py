import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

PARIS_TZ = ZoneInfo("Europe/Paris")
API_URL = "https://v3.football.api-sports.io/fixtures"
WORLD_CUP_LEAGUE_ID = "1"
SEASON = "2026"

TEAM_FR = {
    "Mexico": ("Mexique", "🇲🇽"),
    "South Africa": ("Afrique du Sud", "🇿🇦"),
    "Canada": ("Canada", "🇨🇦"),
    "Qatar": ("Qatar", "🇶🇦"),
    "Brazil": ("Brésil", "🇧🇷"),
    "Morocco": ("Maroc", "🇲🇦"),
    "United States": ("États-Unis", "🇺🇸"),
    "USA": ("États-Unis", "🇺🇸"),
    "France": ("France", "🇫🇷"),
    "Spain": ("Espagne", "🇪🇸"),
    "Portugal": ("Portugal", "🇵🇹"),
    "Germany": ("Allemagne", "🇩🇪"),
    "England": ("Angleterre", "🏴"),
    "Argentina": ("Argentine", "🇦🇷"),
    "Belgium": ("Belgique", "🇧🇪"),
    "Netherlands": ("Pays-Bas", "🇳🇱"),
    "Croatia": ("Croatie", "🇭🇷"),
    "Uruguay": ("Uruguay", "🇺🇾"),
    "Japan": ("Japon", "🇯🇵"),
    "Korea Republic": ("Corée du Sud", "🇰🇷"),
    "South Korea": ("Corée du Sud", "🇰🇷"),
    "Iran": ("Iran", "🇮🇷"),
    "Saudi Arabia": ("Arabie saoudite", "🇸🇦"),
    "Australia": ("Australie", "🇦🇺"),
    "Tunisia": ("Tunisie", "🇹🇳"),
    "Egypt": ("Égypte", "🇪🇬"),
    "Senegal": ("Sénégal", "🇸🇳"),
    "Ghana": ("Ghana", "🇬🇭"),
    "Ivory Coast": ("Côte d’Ivoire", "🇨🇮"),
    "Côte d'Ivoire": ("Côte d’Ivoire", "🇨🇮"),
    "Algeria": ("Algérie", "🇩🇿"),
    "Norway": ("Norvège", "🇳🇴"),
    "Switzerland": ("Suisse", "🇨🇭"),
    "Austria": ("Autriche", "🇦🇹"),
    "Scotland": ("Écosse", "🏴"),
    "New Zealand": ("Nouvelle-Zélande", "🇳🇿"),
    "Paraguay": ("Paraguay", "🇵🇾"),
    "Colombia": ("Colombie", "🇨🇴"),
    "Ecuador": ("Équateur", "🇪🇨"),
    "Panama": ("Panama", "🇵🇦"),
    "Haiti": ("Haïti", "🇭🇹"),
    "Honduras": ("Honduras", "🇭🇳"),
    "Cape Verde": ("Cap-Vert", "🇨🇻"),
    "Czech Republic": ("République tchèque", "🇨🇿"),
    "Czechia": ("République tchèque", "🇨🇿"),
    "Bosnia & Herzegovina": ("Bosnie-Herzégovine", "🇧🇦"),
    "Bosnia and Herzegovina": ("Bosnie-Herzégovine", "🇧🇦"),
    "Curaçao": ("Curaçao", "🇨🇼"),
    "Curacao": ("Curaçao", "🇨🇼"),
    "Uzbekistan": ("Ouzbékistan", "🇺🇿"),
    "Jordan": ("Jordanie", "🇯🇴"),
    "Iraq": ("Irak", "🇮🇶"),
    "DR Congo": ("RD Congo", "🇨🇩"),
    "Congo DR": ("RD Congo", "🇨🇩"),
    "Turkey": ("Turquie", "🇹🇷"),
    "Türkiye": ("Turquie", "🇹🇷"),
    "Sweden": ("Suède", "🇸🇪"),
}

STATUS_FR = {
    "NS": "À venir", "TBD": "À confirmer", "1H": "En direct - 1re mi-temps",
    "HT": "Mi-temps", "2H": "En direct - 2e mi-temps", "ET": "Prolongation",
    "BT": "Pause prolongation", "P": "Tirs au but", "SUSP": "Suspendu", "INT": "Interrompu",
    "FT": "Terminé", "AET": "Terminé après prolongation", "PEN": "Terminé aux tirs au but",
    "PST": "Reporté", "CANC": "Annulé", "ABD": "Abandonné", "AWD": "Décision administrative", "WO": "Forfait",
}
LIVE_STATUSES = {"1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT"}
FINISHED_STATUSES = {"FT", "AET", "PEN"}

def clean_text(text):
    return str(text).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

def format_ics_datetime(dt):
    return dt.strftime("%Y%m%dT%H%M%S")

def team_name_and_flag(name, fallback_flag="🏳️"):
    if not name:
        return "Équipe à confirmer", fallback_flag
    return TEAM_FR.get(name, (name, fallback_flag))

def fetch_api_matches():
    api_key = os.environ.get("FOOTBALL_API_KEY", "").strip()
    if not api_key:
        print("FOOTBALL_API_KEY manquant : utilisation de matches.json")
        return []
    params = urllib.parse.urlencode({"league": WORLD_CUP_LEAGUE_ID, "season": SEASON, "timezone": "Europe/Paris"})
    request = urllib.request.Request(f"{API_URL}?{params}", headers={"x-apisports-key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"Erreur API-Football : {exc} | utilisation de matches.json")
        return []
    fixtures = data.get("response", [])
    errors = data.get("errors")
    if errors:
        print(f"Erreurs API-Football : {errors}")
    print(f"Matchs récupérés depuis API-Football : {len(fixtures)}")
    return fixtures

def load_fallback_matches():
    with open("matches.json", "r", encoding="utf-8") as f:
        return json.load(f)

def make_event_from_api(item, index):
    fixture = item.get("fixture", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    status = fixture.get("status", {}) or {}
    fixture_id = fixture.get("id", index)
    raw_date = fixture.get("date")
    start = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).astimezone(PARIS_TZ)
    end = start + timedelta(hours=2)
    home_raw = (teams.get("home") or {}).get("name")
    away_raw = (teams.get("away") or {}).get("name")
    home, home_flag = team_name_and_flag(home_raw)
    away, away_flag = team_name_and_flag(away_raw)
    home_goals = goals.get("home")
    away_goals = goals.get("away")
    status_short = status.get("short", "NS")
    status_text = STATUS_FR.get(status_short, status.get("long", status_short))
    if status_short in LIVE_STATUSES:
        score = f" {home_goals}-{away_goals} " if home_goals is not None and away_goals is not None else " - "
        title = f"🔴 {home_flag} {home}{score}{away_flag} {away}"
    elif status_short in FINISHED_STATUSES:
        score = f" {home_goals}-{away_goals} " if home_goals is not None and away_goals is not None else " - "
        title = f"✅ {home_flag} {home}{score}{away_flag} {away}"
    elif status_short in {"PST", "CANC", "ABD", "AWD", "WO"}:
        title = f"⚠️ {home_flag} {home} - {away_flag} {away} ({status_text})"
    else:
        title = f"{home_flag} {home} - {away_flag} {away}"
    venue = fixture.get("venue", {}) or {}
    venue_name = venue.get("name") or ""
    venue_city = venue.get("city") or ""
    location = ", ".join([p for p in [venue_name, venue_city] if p])
    description = f"Statut : {status_text}"
    if home_goals is not None and away_goals is not None:
        description += f"\nScore : {home} {home_goals}-{away_goals} {away}"
    return {"uid": f"api-football-worldcup2026-{fixture_id}@github-calendar", "start": start, "end": end, "title": title, "location": location, "description": description}

def make_event_from_fallback(match, index):
    start = datetime.fromisoformat(f"{match['date']}T{match['time']}:00").replace(tzinfo=PARIS_TZ)
    end = start + timedelta(hours=2)
    title = f"{match.get('home_flag', '🏳️')} {match['home']} - {match.get('away_flag', '🏳️')} {match['away']}"
    return {"uid": f"worldcup2026-{index}-{match['date']}-{match['time'].replace(':', '')}@github-calendar", "start": start, "end": end, "title": title, "location": match.get("stadium", ""), "description": f"Rappel : {title}"}

def build_calendar(events):
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//World Cup 2026 Calendar//FR//", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Matchs 2026", "X-WR-TIMEZONE:Europe/Paris"]
    for event in events:
        lines.extend([
            "BEGIN:VEVENT", f"UID:{event['uid']}", f"DTSTAMP:{now_utc}",
            f"DTSTART;TZID=Europe/Paris:{format_ics_datetime(event['start'])}",
            f"DTEND;TZID=Europe/Paris:{format_ics_datetime(event['end'])}",
            f"SUMMARY:{clean_text(event['title'])}", f"LOCATION:{clean_text(event['location'])}",
            f"DESCRIPTION:{clean_text(event['description'])}", "BEGIN:VALARM", "TRIGGER:-PT1H", "ACTION:DISPLAY",
            f"DESCRIPTION:Rappel : {clean_text(event['title'])}", "END:VALARM", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

def main():
    api_matches = fetch_api_matches()
    if api_matches:
        events = [make_event_from_api(item, i) for i, item in enumerate(api_matches, start=1)]
        events.sort(key=lambda event: event["start"])
        print("Calendrier créé avec API-Football")
    else:
        fallback_matches = load_fallback_matches()
        events = [make_event_from_fallback(match, i) for i, match in enumerate(fallback_matches, start=1)]
        print("Calendrier créé avec matches.json")
    with open("worldcup2026.ics", "w", encoding="utf-8") as f:
        f.write(build_calendar(events))

if __name__ == "__main__":
    main()
