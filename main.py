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

# -------- API FOREX FACTORY --------
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

res = requests.get(url)

if res.status_code != 200:
    print("Erro API")
    exit()

events = res.json()

print("Eventos recebidos:", len(events))

# -------- PROCESSAR DADOS --------
data = []

for event in events:
    try:
        impact = str(event.get("impact", "")).upper()
        title = event.get("title", "").upper()

        # pegar horário
        time = event.get("time") or event.get("date") or "N/A"

        # -------- DETECTAR MOEDA (INTELIGENTE) --------
        if any(x in title for x in ["USD", "FED", "PCE", "CPI", "GDP", "UNEMPLOYMENT", "HOME SALES"]):
            currency = "USD"

        elif any(x in title for x in ["EUR", "ECB", "GERMAN"]):
            currency = "EUR"

        elif any(x in title for x in ["JPY", "BOJ", "TOKYO"]):
            currency = "JPY"

        elif any(x in title for x in ["GBP", "BOE"]):
            currency = "GBP"

        elif any(x in title for x in ["AUD", "RBA"]):
            currency = "AUD"

        elif any(x in title for x in ["NZD", "RBNZ"]):
            currency = "NZD"

        elif any(x in title for x in ["CAD", "BOC"]):
            currency = "CAD"

        elif any(x in title for x in ["CHF", "SNB"]):
            currency = "CHF"

        else:
            currency = "N/A"

        # -------- FILTRO IMPACTO --------
        if "3" in impact or "HIGH" in impact:
            impact_text = "HIGH"
        elif "2" in impact or "MEDIUM" in impact:
            impact_text = "MEDIUM"
        else:
            continue

        data.append([time, currency, impact_text, title])

    except Exception as e:
        print("Erro:", e)

# -------- ENVIAR PARA PLANILHA --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

if len(data) == 0:
    print("❌ Nenhum dado encontrado")
else:
    sheet.append_rows(data)

print(f"✅ {len(data)} eventos enviados com sucesso 🚀")
