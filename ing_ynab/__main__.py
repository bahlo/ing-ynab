"""ing_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
from datetime import datetime
from time import sleep
from decimal import Decimal
from hashlib import sha256
from typing import Optional, NoReturn, List, Dict
import logging
import os
import sys
from getpass import getpass
from dotenv import load_dotenv
from fints.client import FinTS3PinTanClient
from fints.models import SEPAAccount
import requests
from mt940.models import Transaction as FinTSTransaction

YNAB_BASE_URL = "https://api.youneedabudget.com/v1"

# https://github.com/PyCQA/pylint/issues/647
# pylint: disable=C0330


def hash_transaction(transaction: FinTSTransaction) -> str:
    """Generate a hash for the transaction to make them identifiable.
    """
    data = transaction.data
    payload = "%s:%s:%s:%s" % (
        data["date"],
        data["applicant_name"],
        data["purpose"],
        data["amount"],
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def transform_transactions(
    transactions: List[FinTSTransaction],
    account_id: str,
    flag_color: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Transform the FinTS transactions into something the YNAB API understands.
    """
    transformed = []
    for transaction in transactions:
        data = transaction.data
        transformed.append(
            {
                "account_id": account_id,
                "date": data["date"].isoformat(),
                "amount": int(data["amount"].amount * Decimal("1000.0")),
                "payee_name": data["applicant_name"],
                "cleared": "cleared",
                "memo": data["purpose"],
                "flag_color": flag_color,
            }
        )
    return transformed


def import_transactions(
    ynab_transactions: List[Dict[str, str]],
    ynab_access_token: str,
    ynab_budget_id: str,
) -> List[int]:
    """Import the transaction into YNAB, returns an array with transaction ids.

    :param transactions: An array of transactions.
    """
    headers = {"Authorization": "Bearer " + ynab_access_token}
    payload = {
        "transactions": ynab_transactions,
    }
    path = "/budgets/" + ynab_budget_id + "/transactions"
    response = requests.post(YNAB_BASE_URL + path, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["transaction_ids"]


def ing_to_ynab(
    fints_client: FinTS3PinTanClient,
    fints_account: SEPAAccount,
    ynab_access_token: str,
    debug: bool = False,
) -> NoReturn:
    """This code is called in a predefined interval to add new ing transactions into ynab.
    """
    # Try to read from state
    start_date = None
    last_hash = None
    try:
        with open("state", "r") as state_file:
            contents = state_file.read().splitlines()
            start_date = datetime.fromisoformat(contents[0])
            last_hash = contents[1]
    except:  # pylint: disable=bare-except
        start_date_env = os.environ.get("START_DATE")
        if start_date_env is not None:
            start_date = datetime.fromisoformat(start_date_env)
        else:
            start_date = datetime.now()

    transactions = fints_client.get_transactions(fints_account, start_date=start_date)

    # Figure out where to start by finding the last transaction.
    array_start = 0
    for i, transaction in enumerate(transactions):
        if hash_transaction(transaction) == last_hash:
            array_start = i + 1
    transactions = transactions[array_start:]

    if len(transactions) == 0:
        print("No new transactions found")
        return

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = transform_transactions(
        transactions,
        os.environ["YNAB_ACCOUNT_ID"],
        flag_color=os.environ.get("YNAB_FLAG_COLOR"),
    )

    # Print or import the transformed transactions.
    if debug:
        for transaction in ynab_transactions:
            print(transaction)
    else:
        imported = import_transactions(
            ynab_transactions, ynab_access_token, os.environ["YNAB_BUDGET_ID"],
        )
        print("Imported %d new transaction(s)" % len(imported))

    with open("state", "w") as state_file:
        state_file.write(
            "%s\n%s"
            % (datetime.now().strftime("%Y-%m-%d"), hash_transaction(transactions[0]))
        )


def main() -> NoReturn:
    """This is the main function
    """
    load_dotenv()

    debug = os.environ.get("DEBUG") == "1"
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    fints_pin = os.environ.get("FINTS_PIN")
    if fints_pin is None:
        fints_pin = getpass("FinTS pin: ")

    fints_client = FinTS3PinTanClient(
        "50010517",  # BLZ
        os.environ["FINTS_LOGIN"],
        fints_pin,
        "https://fints.ing-diba.de/fints/",  # Endpoint
        product_id=os.environ.get("FINTS_PRODUCT_ID", None),
    )
    if fints_client.init_tan_response:
        print("TAN required:", fints_client.init_tan_response.challenge)
        tan = input("Please enter TAN:")
        fints_client.send_tan(fints_client.init_tan_response, tan)

    accounts = fints_client.get_sepa_accounts()

    selected_account = None
    for account in accounts:
        if account.iban == os.environ["FINTS_IBAN"]:
            selected_account = account
            break
    if selected_account is None:
        print("Could not find account, is the IBAN correct?")
        print("Available accounts: %s" % accounts)
        sys.exit(1)

    interval = int(os.environ.get("SLEEP_INTERVAL", "300"))
    ynab_access_token = os.environ.get("YNAB_ACCESS_TOKEN")
    if ynab_access_token is None:
        ynab_access_token = getpass("YNAB Access Token: ")

    while True:
        ing_to_ynab(fints_client, selected_account, ynab_access_token, debug=debug)
        print("Sleeping for %d seconds" % interval)
        sleep(interval)


if __name__ == "__main__":
    main()
