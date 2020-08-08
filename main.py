"""fints_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
from datetime import datetime
import logging
import os
from getpass import getpass
from dotenv import load_dotenv
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap
import requests

BASE_URL = "https://api.youneedabudget.com/v1"

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    fints_client = FinTS3PinTanClient(
        os.environ["FINTS_BLZ"],
        os.environ["FINTS_LOGIN"],
        os.environ.get("FINTS_PIN", getpass("PIN: ")),
        os.environ["FINTS_ENDPOINT"],
        product_id=os.environ.get("FINTS_PRODUCT_ID", None),
    )
    minimal_interactive_cli_bootstrap(fints_client)
    with fints_client:
        if fints_client.init_tan_response:
            print("TAN required:", fints_client.init_tan_response.challenge)
            tan = input("Please enter TAN:")
            fints_client.send_tan(fints_client.init_tan_response, tan)

        accounts = fints_client.get_sepa_accounts()
        transactions = fints_client.get_transactions(
            accounts[0], start_date=datetime.now()
        )
        print(transactions)
        # TODO: Convert transactions to a format YNAB will accept.
        # TODO: ynab.import_transactions(transactions)


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
