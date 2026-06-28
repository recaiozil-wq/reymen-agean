import json

path = r'C:\Users\marko\AppData\Local\ReYMeN\gateway_state.json'

state = {
    'pid': None,
    'kind': 'ReYMeN-gateway',
    'gateway_state': 'stopped',
    'platforms': {
        'telegram': {
            'state': 'disconnected',
            'error_code': None,
            'error_message': None
        }
    }
}

with open(path, 'w') as f:
    json.dump(state, f)

print('Gateway state reset OK')
print('State:', json.dumps(state))
