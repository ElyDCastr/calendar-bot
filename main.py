import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json

# -------- GOOGLE AUTH --------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1paBlA499_ZIlfAHto-8-u4z3O8QVSwsqfbJJivnDNGo/edit").sheet1

# -------- REQUEST --------
url = "https://www.forexfactory.com/calendar"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers)

soup = BeautifulSoup(res.text, "html.parser")

events = soup.select("tr.calendar__row")

data = []

for event in events:
    try:
        time = event.select_one(".calendar__time").text.strip()
        currency = event.select_one(".calendar__currency").text.strip()
        title = event.select_one(".calendar__event").text.strip()

        impact_span = event.select_one(".calendar__impact span")

        if impact_span:
            impact = impact_span["title"]  # Ex: High Impact Expected

            # FILTRO 🔥
            if "Medium" in impact or "High" in impact:
                data.append([time, currency, impact, title])

    except:
        pass

# -------- ENVIAR PARA SHEETS --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

for row in data:
    sheet.append_row(row)

print(f"{len(data)} eventos enviados 🚀")
