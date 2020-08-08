import os
import requests

BASE_URL = "https://api.youneedabudget.com/v1"


def import_transactions(transactions):
    # Import the transaction into YNAB, returns the number of imported
    # transactions
    headers = {"Authorization": "Bearer " + os.environ["YNAB_ACCESS_TOKEN"]}
    payload = {
        "transactions": transactions,
    }
    path = "/budgets/" + os.environ["YNAB_BUDGET_ID"] + "/transactions"
    r = requests.post(BASE_URL + path, json=payload, headers=headers)
    r.raise_for_status()
