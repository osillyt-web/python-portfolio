import urllib.request, json

url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=20) as r:
    данные = json.loads(r.read().decode('utf-8'))

for валюта in данные:
    if валюта["cc"] == "GBP":
        print("Курс фунта:", валюта["rate"])