"""
This module contains the core business logic.
"""
from datetime import datetime
from time import sleep
from typing import NoReturn, Optional
import logging
import os
import sys
from getpass import getpass
from dotenv import load_dotenv

from ynab import YNABClient
from ing import INGClient, AccountNotFoundException, hash_transaction
from state import State


def ing_to_ynab(
    state: State,
    ing_client: INGClient,
    ynab_client: YNABClient,
    ynab_flag_color: Optional[str] = None,
    start_date_config: Optional[datetime] = None,
    debug: bool = False,
) -> NoReturn:
    """
    This code is called in a predefined interval to add new ing transactions
    into ynab.
    """
    start_date, last_hash = state.restore(start_date_config)

    transactions = ing_client.get_transactions(
        start_date=start_date, last_hash=last_hash
    )

    if len(transactions) == 0:
        print("No new transactions found")
        return

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = ynab_client.transform_transactions(
        transactions, flag_color=ynab_flag_color,
    )

    # Print or import the transformed transactions.
    if debug:
        for transaction in ynab_transactions:
            print(transaction)
    else:
        imported = ynab_client.import_transactions(ynab_transactions)
        print("Imported %d new transaction(s)" % len(imported))

    state.store(hash_transaction(transactions[len(transactions) - 1]))


def main() -> NoReturn:
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

    start_date = None
    start_date_env = os.environ.get("START_DATE")
    if start_date_env is not None:
        start_date = datetime.fromisoformat(start_date_env)

    interval = int(os.environ.get("SLEEP_INTERVAL", "300"))

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
        sys.exit(1)

    ynab_client = YNABClient(ynab_access_token, ynab_account_id, ynab_budget_id)

    state = State("state")

    # Import new statements into YNAB every n minutes
    while True:
        ing_to_ynab(
            state,
            ing_client,
            ynab_client,
            start_date_config=start_date,
            ynab_flag_color=ynab_flag_color,
            debug=debug,
        )
        print("Sleeping for %d seconds" % interval)
        sleep(interval)


if __name__ == "__main__":
    main()
