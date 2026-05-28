import requests
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

# -------- PEGAR DADOS (API INTERNA) --------
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

res = requests.get(url)

if res.status_code != 200:
    print("Erro ao acessar API")
    exit()

events = res.json()

data = []

for event in events:
    impact = event.get("impact")

    # FILTRO: médio (2) e alto (3)
    if impact in [2, 3]:
        time = event.get("time")
        currency = event.get("currency")
        title = event.get("title")

        # transformar impacto em texto
        if impact == 3:
            impact_text = "HIGH"
        elif impact == 2:
            impact_text = "MEDIUM"

        data.append([time, currency, impact_text, title])

# -------- ENVIAR PARA SHEETS --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

for row in data:
    sheet.append_row(row)

print(f"{len(data)} eventos enviados 🚀")
