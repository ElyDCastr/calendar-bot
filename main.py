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

# -------- PEGAR DADOS --------
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers)

if res.status_code != 200:
    print("Erro ao acessar API")
    exit()

events = res.json()

print(f"Total de eventos recebidos: {len(events)}")

# -------- PROCESSAR DADOS --------
data = []

for event in events:
    try:
        impact = str(event.get("impact", ""))
        time = event.get("time", "").strip()
        currency = event.get("currency", "").strip()
        title = event.get("title", "").strip()

        # FILTRO DE IMPACTO (médio e alto)
        if ("2" in impact) or ("3" in impact) or ("Medium" in impact) or ("High" in impact):

            # IGNORAR eventos sem dados importantes
            if time == "" or currency == "":
                continue

            # PADRONIZAR IMPACTO
            if "3" in impact or "High" in impact:
                impact_text = "HIGH"
            elif "2" in impact or "Medium" in impact:
                impact_text = "MEDIUM"
            else:
                continue

            data.append([time, currency, impact_text, title])

    except Exception as e:
        print("Erro:", e)

# -------- ENVIAR PARA SHEETS --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

if len(data) == 0:
    print("⚠️ Nenhum evento válido encontrado")
else:
    for row in data:
        sheet.append_row(row)

print(f"{len(data)} eventos enviados 🚀")
