import json, urllib.request, urllib.parse

with open(r'C:\Users\marko\AppData\Local\ReYMeN\.env') as f:
    for line in f:
        line = line.strip()
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            token = line.split('=', 1)[1]
            break

data = urllib.parse.urlencode({
    'chat_id': '6328823909',
    'text': 'ReYMeN test - API dogrudan calisiyor'
}).encode()

r = urllib.request.urlopen(f'https://api.telegram.org/bot{token}/sendMessage', data=data)
result = json.loads(r.read())
print(json.dumps(result, indent=2))
