import json
import os
import requests

BASE_URL = 'https://api.youneedabudget.com/v1'

class TransactionCreationFailed(Exception):
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
    def __str__(self):
        return "Unexpeced status code %d: %s" % (self.status_code, self.text)

def import_transactions(transactions):
    headers = {'Authorization': "Bearer "+os.environ['YNAB_ACCESS_TOKEN']}
    payload = {
        'transactions': transactions,
    }
    path = '/budgets/'+os.environ['YNAB_BUDGET_ID']+'/transactions'
    r = requests.post(BASE_URL + path, json=payload, headers=headers)
    if r.status_code != 201:
        raise TransactionCreationFailed(r.status_code, r.json)
