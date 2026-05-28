import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json
from datetime import datetime

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

data = []

for event in events:
    try:
        impact = str(event.get("impact", "")).upper()
        title = event.get("title", "").title()
        raw_time = event.get("time") or event.get("date")

        if not raw_time:
            continue

        # -------- DATA / HORA --------
        dt = datetime.fromisoformat(raw_time.replace("Z", ""))
        day = dt.strftime("%a")       # Tue, Wed
        time = dt.strftime("%H:%M")   # 08:30

        # -------- MOEDA --------
        t = title.upper()

        if any(x in t for x in ["USD", "FED", "PCE", "CPI", "GDP", "UNEMPLOYMENT", "HOME SALES"]):
            currency = "USD"
        elif any(x in t for x in ["EUR", "ECB", "GERMAN"]):
            currency = "EUR"
        elif any(x in t for x in ["JPY", "BOJ", "TOKYO"]):
            currency = "JPY"
        elif any(x in t for x in ["GBP", "BOE"]):
            currency = "GBP"
        elif any(x in t for x in ["AUD", "RBA"]):
            currency = "AUD"
        elif any(x in t for x in ["NZD", "RBNZ"]):
            currency = "NZD"
        elif any(x in t for x in ["CAD", "BOC"]):
            currency = "CAD"
        elif any(x in t for x in ["CHF", "SNB"]):
            currency = "CHF"
        else:
            currency = "🌍"

        # -------- IMPACTO (ESTILO INVESTING) --------
        if "3" in impact or "HIGH" in impact:
            impact_text = "🔴🔴🔴"
        elif "2" in impact or "MEDIUM" in impact:
            impact_text = "🔴🔴"
        else:
            continue

        data.append([day, time, currency, impact_text, title])

    except Exception as e:
        print("Erro:", e)

# -------- ORDENAR POR DIA E HORA --------
data.sort(key=lambda x: (x[0], x[1]))

# -------- ENVIAR --------
sheet.clear()
sheet.append_row(["Day", "Time", "Currency", "Impact", "Event"])

if data:
    sheet.append_rows(data)

print(f"✅ {len(data)} eventos enviados estilo Investing 🚀")
