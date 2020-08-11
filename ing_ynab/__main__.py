"""
ing_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
from datetime import datetime
from time import sleep
from typing import NoReturn, Optional
import logging
import os
import sys
from getpass import getpass
from dotenv import load_dotenv

import ynab
from ing import INGClient, AccountNotFoundException, hash_transaction

# https://github.com/PyCQA/pylint/issues/647
# pylint: disable=C0330


def ing_to_ynab(
    ing_client: INGClient,
    ynab_access_token: str,
    ynab_account_id: str,
    ynab_budget_id: str,
    ynab_flag_color: Optional[str] = None,
    start_date_config: Optional[datetime] = None,
    debug: bool = False,
) -> NoReturn:
    """
    This code is called in a predefined interval to add new ing transactions into ynab.
    """
    start_date = None
    last_hash = None
    try:
        with open("state", "r") as state_file:
            contents = state_file.read().splitlines()
            start_date = datetime.fromisoformat(contents[0])
            last_hash = contents[1]
    except:  # pylint: disable=bare-except
        start_date = start_date_config

    transactions = ing_client.get_transactions(
        start_date=start_date, last_hash=last_hash
    )

    if len(transactions) == 0:
        print("No new transactions found")
        return

    # Transform FinTS transactions to YNAB transactions.
    ynab_transactions = ynab.transform_transactions(
        transactions, ynab_account_id, flag_color=ynab_flag_color,
    )

    # Print or import the transformed transactions.
    if debug:
        for transaction in ynab_transactions:
            print(transaction)
    else:
        imported = ynab.import_transactions(
            ynab_transactions, ynab_access_token, os.environ["YNAB_BUDGET_ID"],
        )
        print("Imported %d new transaction(s)" % len(imported))

    with open("state", "w") as state_file:
        state_file.write(
            "%s\n%s"
            % (datetime.now().strftime("%Y-%m-%d"), hash_transaction(transactions[0]),)
        )


def main() -> NoReturn:
    """
    This is the main function
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

    # Import new statements into YNAB every n minutes
    while True:
        ing_to_ynab(
            ing_client,
            ynab_access_token,
            ynab_account_id,
            ynab_budget_id,
            start_date_config=start_date,
            ynab_flag_color=ynab_flag_color,
            debug=debug,
        )
        print("Sleeping for %d seconds" % interval)
        sleep(interval)


if __name__ == "__main__":
    main()
