"""ing_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
from datetime import datetime
from time import sleep
from decimal import Decimal
import logging
import os
from getpass import getpass
from dotenv import load_dotenv
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap
import requests

YNAB_BASE_URL = "https://api.youneedabudget.com/v1"


def transform_transactions(transactions, account_id=None):
    transformed = []
    for transaction in transactions:
        data = transaction.data
        amount_decimal = data["amount"].amount * Decimal("1000.0")
        transformed.append(
            {
                "account_id": account_id,
                "date": data["date"].isoformat(),
                "amount": int(amount_decimal),
                "payee_name": data["applicant_name"],
                "cleared": "cleared",
                "memo": data["purpose"],
            },
        )
    return transformed


def import_transactions(transactions, access_token=None, budget_id=None):
    """Import the transaction into YNAB, returns an array with transaction ids.

    :param transactions: An array of transactions.
    """
    headers = {"Authorization": "Bearer " + access_token}
    payload = {
        "transactions": transactions,
    }
    path = "/budgets/" + budget_id + "/transactions"
    response = requests.post(YNAB_BASE_URL + path, json=payload, headers=headers)
    print(response.json())
    response.raise_for_status()
    return response.json()["data"]["transaction_ids"]


def ing_to_ynab(
    fints_client=None,
    fints_account=None,
    start_date=None,
    ynab_account_id=None,
    ynab_access_token=None,
    ynab_budget_id=None,
    debug=None,
):
    """This code is called in a predefined interval to add new ing transactions into ynab.
    """
    transactions = fints_client.get_transactions(
        fints_account, start_date=datetime.fromisoformat(start_date)
    )

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = transform_transactions(transactions, account_id=ynab_account_id)

    # Print or import the transformed transactions.
    if debug:
        for transaction in ynab_transactions:
            print(transaction)
    else:
        import_transactions(
            ynab_transactions, access_token=ynab_access_token, budget_id=ynab_budget_id,
        )


if __name__ == "__main__":
    load_dotenv()

    # Initialize FinTS.
    fints_client = FinTS3PinTanClient(
        "50010517",  # BLZ
        os.environ["FINTS_LOGIN"],
        os.environ.get("FINTS_PIN", getpass("PIN: ")),
        "https://fints.ing-diba.de/fints/",  # Endpoint
        product_id=os.environ.get("FINTS_PRODUCT_ID", None),
    )
    if fints_client.init_tan_response:
        print("TAN required:", fints_client.init_tan_response.challenge)
        tan = input("Please enter TAN:")
        fints_client.send_tan(fints_client.init_tan_response, tan)

    # Get sepa accounts.
    accounts = fints_client.get_sepa_accounts()

    # Find selected one.
    selected_account = None
    for account in accounts:
        if account.iban == os.environ["FINTS_IBAN"]:
            selected_account = account
            break
    if selected_account == None:
        print("Could not find account, is the IBAN correct?")
        print("Available accounts: %s" % accounts)
        exit(1)

    interval = int(os.environ.get("SLEEP_INTERVAL", "300"))

    while True:
        ing_to_ynab(
            fints_client=fints_client,
            fints_account=selected_account,
            ynab_access_token=os.environ["YNAB_ACCESS_TOKEN"],
            ynab_account_id=os.environ["YNAB_ACCOUNT_ID"],
            ynab_budget_id=os.environ["YNAB_BUDGET_ID"],
            start_date=os.environ.get("START_DATE", datetime.now()),
            debug=os.environ.get("DEBUG") == "1",
        )

        sleep(interval)
