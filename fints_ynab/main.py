"""fints_ynab is a simple tool to add data from German banks to YNAB via FinTS.
"""
import logging
import os
from getpass import getpass
from dotenv import load_dotenv
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap

# import ynab

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

        print(fints_client.get_sepa_accounts())
