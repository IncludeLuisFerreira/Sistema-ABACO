import json
import urllib.request
import urllib.error

url = 'http://localhost:8000/api/v1/auth/login'
data = json.dumps({
    'email': 'admin@abaco.org.br',
    'senha': 'ABACOadmin2026'
}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    try:
        print(e.read().decode('utf-8'))
    except:
        pass
except Exception as e:
    print('ERROR', str(e))
