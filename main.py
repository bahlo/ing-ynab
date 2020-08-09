"""ing_ynab is a simple tool to add data from German banks to YNAB via FinTS.
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


if __name__ == "__main__":
    load_dotenv()

    # Initialize FinTS.
    fints_client = FinTS3PinTanClient(
        "50010517",
        os.environ["FINTS_LOGIN"],
        os.environ.get("FINTS_PIN", getpass("PIN: ")),
        "https://fints.ing-diba.de/fints/",
        product_id=os.environ.get("FINTS_PRODUCT_ID", None),
    )
    if fints_client.init_tan_response:
        print("TAN required:", fints_client.init_tan_response.challenge)
        tan = input("Please enter TAN:")
        fints_client.send_tan(fints_client.init_tan_response, tan)

    # Get sepa accounts.
    accounts = fints_client.get_sepa_accounts()

    # Find selected one.
    selected_acocunt = None
    for account in accounts:
        if account.iban == os.environ["FINTS_IBAN"]:
            selected_acocunt = account
            break
    if selected_acocunt == None:
        print("Could not find account, is the IBAN correct?")
        exit(1)

    start_date = os.environ.get("START_DATE", datetime.now())
    transactions = fints_client.get_transactions(
        selected_acocunt, start_date=datetime.fromisoformat(start_date)
    )

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = transform_transactions(
        transactions, account_id=os.environ["YNAB_ACCOUNT_ID"]
    )

    # Print or import the transformed transactions.
    if os.environ.get("DEBUG", "") == "1":
        for transaction in ynab_transactions:
            print(transaction)
    else:
        import_transactions(
            ynab_transactions,
            access_token=os.environ["YNAB_ACCESS_TOKEN"],
            budget_id=os.environ["YNAB_BUDGET_ID"],
        )
