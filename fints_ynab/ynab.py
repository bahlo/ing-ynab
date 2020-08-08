"""The YNAB module holds code to interact with the YNAB API (v1).
"""
import os
import requests

BASE_URL = "https://api.youneedabudget.com/v1"


def import_transactions(transactions):
    """Import the transaction into YNAB, returns an array with transaction ids.

    :param transactions: An array of transactions.
    """
    headers = {"Authorization": "Bearer " + os.environ["YNAB_ACCESS_TOKEN"]}
    payload = {
        "transactions": transactions,
    }
    path = "/budgets/" + os.environ["YNAB_BUDGET_ID"] + "/transactions"
    response = requests.post(BASE_URL + path, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["transaction_ids"]
