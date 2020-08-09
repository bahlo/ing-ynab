"""fints_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
from datetime import datetime
from decimal import Decimal
import logging
import os
from getpass import getpass
from dotenv import load_dotenv
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap
import requests

YNAB_BASE_URL = "https://api.youneedabudget.com/v1"


def transform_transactions(transactions):
    transformed = []
    for transaction in transactions:
        data = transaction.data
        amount_decimal = data["amount"].amount * Decimal("1000.0")
        transformed.append(
            {
                "date": data["date"].isoformat(),
                "amount": int(amount_decimal),
                "payee_name": data["applicant_name"],
                "cleared": "cleared",
            }
        )
    return transformed


def import_transactions(transactions):
    """Import the transaction into YNAB, returns an array with transaction ids.

    :param transactions: An array of transactions.
    """
    headers = {"Authorization": "Bearer " + os.environ["YNAB_ACCESS_TOKEN"]}
    payload = {
        "transactions": transactions,
    }
    path = "/budgets/" + os.environ["YNAB_BUDGET_ID"] + "/transactions"
    response = requests.post(YNAB_BASE_URL + path, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["transaction_ids"]


if __name__ == "__main__":
    load_dotenv()

    fints_client = FinTS3PinTanClient(
        os.environ["FINTS_BLZ"],
        os.environ["FINTS_LOGIN"],
        os.environ.get("FINTS_PIN", getpass("PIN: ")),
        os.environ["FINTS_ENDPOINT"],
        product_id=os.environ.get("FINTS_PRODUCT_ID", None),
    )
    if fints_client.init_tan_response:
        print("TAN required:", fints_client.init_tan_response.challenge)
        tan = input("Please enter TAN:")
        fints_client.send_tan(fints_client.init_tan_response, tan)

    accounts = fints_client.get_sepa_accounts()
    transactions = fints_client.get_transactions(
        accounts[2], start_date=datetime.fromisoformat("2020-08-08")
    )
    ynab_transactions = transform_transactions(transactions)
    if os.environ.get("DEBUG", "") == "1":
        for transaction in ynab_transactions:
            print(transaction)
    else:
        import_transactions(ynab_transactions)
