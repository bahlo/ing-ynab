"""
This module contains the core business logic.
"""
from datetime import date, timedelta
from time import sleep
from typing import NoReturn
import logging
import os
import sys
from getpass import getpass
from dotenv import load_dotenv

from ing_ynab.ynab import YNABClient, YNABError
from ing_ynab.ing import INGClient, AccountNotFoundException


def ing_to_ynab(
    ing_client: INGClient, ynab_client: YNABClient, debug: bool = False,
) -> NoReturn:
    """
    This code is called in a predefined interval to add new ing transactions
    into ynab.
    """
    start_date = ynab_client.latest_transaction_date()
    if start_date is None:
        start_date = date.today() - timedelta(days=7)

    transactions = ing_client.get_transactions(start_date=start_date)

    if len(transactions) == 0:
        print("No new transactions found")
        return

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = ynab_client.transform_transactions(transactions)

    # Print or import the transformed transactions.
    if debug:
        for transaction in ynab_transactions:
            print(transaction)
    else:
        imported = ynab_client.import_transactions(ynab_transactions)
        print("Imported %d new transaction(s)" % len(imported))


def main() -> int:
    """
    Start the main business logic.
    """
    load_dotenv()

    # Parse environment variables
    debug = os.environ.get("DEBUG") == "1"
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    ing_pin = os.environ.get("ING_PIN")
    if ing_pin is None:
        ing_pin = getpass("ING pin: ")

    ynab_access_token = os.environ.get("YNAB_ACCESS_TOKEN")
    if ynab_access_token is None:
        ynab_access_token = getpass("YNAB Access Token: ")

    ynab_account_id = os.environ["YNAB_ACCOUNT_ID"]
    ynab_budget_id = os.environ["YNAB_BUDGET_ID"]
    ynab_flag_color = os.environ.get("YNAB_FLAG_COLOR")

    sleep_interval = int(os.environ.get("SLEEP_INTERVAL_SECONDS", "300"))

    # Create INGClient
    ing_client = INGClient(
        os.environ["ING_LOGIN"],
        ing_pin,
        fints_product_id=os.environ.get("FINTS_PRODUCT_ID"),
    )

    # Select account with configured IBAN
    try:
        ing_client.select_account(os.environ["ING_IBAN"])
    except AccountNotFoundException as ex:
        print("Could not find account, is the IBAN correct?")
        print("Available accounts: %s" % ex.accounts)
        return 1

    ynab_client = YNABClient(
        ynab_access_token, ynab_account_id, ynab_budget_id, flag_color=ynab_flag_color
    )

    # Import new statements into YNAB every n minutes
    while True:
        try:
            ing_to_ynab(ing_client, ynab_client, debug=debug)
        except YNABError as ex:
            print("Could not import transactions: %s" % ex)
        except KeyboardInterrupt:
            raise  # We need to have this case for ^C to work
        except:  # pylint: disable=bare-except
            print("Unexpected error:", sys.exc_info()[0])
        print("Sleeping for %d seconds" % sleep_interval)
        sleep(sleep_interval)
