from datetime import datetime, date
import json
import os

import requests

BASE_URL = 'https://api.youneedabudget.com/v1'

def default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()

if __name__ == '__main__':
    headers = {'Authorization': "Bearer "+os.environ['YNAB_ACCESS_TOKEN']}
    payload = {
        'transactions': [
            {
                'date': datetime.now(),
                'amount': 13.37,
                'cleared': 'cleared',
                'memo': 'hello from python',
            },
        ],
    }
    json_payload = json.dumps(payload, default=default)
    print(json_payload)
    r = requests.post(BASE_URL + '/budgets/'+os.environ['YNAB_BUDGET_ID']+'/transactions', data=json_payload, headers=headers)
    print(r.json())