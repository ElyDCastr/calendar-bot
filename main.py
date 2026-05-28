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

sheet = client.open("economic_calendar").sheet1

# -------- REQUEST --------
url = "https://www.investing.com/economic-calendar/"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

res = requests.get(url, headers=headers)

if res.status_code != 200:
    print("Erro ao acessar site")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

events = soup.select("tr.js-event-item")

data = []

for event in events:
    stars = event.select(".grayFullBullishIcon")
    if len(stars) >= 2:
        try:
            time = event.select_one(".time").text.strip()
            currency = event.select_one(".currency").text.strip()
            title = event.select_one(".event").text.strip()

            data.append([time, currency, len(stars), title])
        except:
            pass

# -------- ENVIAR PARA SHEETS --------
sheet.clear()
sheet.append_row(["Time", "Currency", "Impact", "Event"])

for row in data:
    sheet.append_row(row)

print("Planilha atualizada!")
