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

# -------- API --------
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

res = requests.get(url)

if res.status_code != 200:
    print("Erro API")
    exit()

events = res.json()

print("Eventos recebidos:", len(events))

# -------- PROCESSAMENTO --------
data = []

for event in events:
    try:
        impact = str(event.get("impact", ""))
        title = event.get("title", "").strip()

        # 🔥 PEGAR CAMPOS CORRETOS
        currency = event.get("currency") or "N/A"
        time = event.get("time") or event.get("date") or "N/A"

        # FILTRO IMPACTO
        if "3" in impact or "High" in impact:
            impact_text = "HIGH"
        elif "2" in impact or "Medium" in impact:
            impact_text = "MEDIUM"
        else:
            continue

        data.append([time, currency, impact_text, title])

    except Exception as e:
        print("Erro:", e)

# -------- ENVIAR --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

if len(data) == 0:
    print("❌ Nenhum dado")
else:
    sheet.append_rows(data)

print(f"✅ {len(data)} eventos enviados")
