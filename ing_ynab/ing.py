"""
Provides classes and functions to work with the ING FinTS API.
"""
import datetime
from typing import Optional, List
from mt940.models import Transaction
from fints.client import FinTS3PinTanClient
from fints.models import SEPAAccount

ING_DE_BLZ = "50010517"
ING_DE_ENDPOINT = "https://fints.ing.de/fints/"


class AccountNotFoundException(Exception):
    """
    Raised if the account could not be found.
    """

    accounts: List[SEPAAccount] = []

    def __init__(self, accounts: List[SEPAAccount]):
        Exception.__init__()
        self.accounts = accounts


class INGClient:
    """
    INGClient provides methods to connect to ING via FinTS.
    """

    fints_client: FinTS3PinTanClient
    selected_account: SEPAAccount

    def __init__(self, login: str, pin: str, fints_product_id: Optional[str] = None):
        self.fints_client = FinTS3PinTanClient(
            ING_DE_BLZ, login, pin, ING_DE_ENDPOINT, product_id=fints_product_id,
        )

    def select_account(self, iban: str) -> None:
        """
        Select the account with the given IBAN.
        """
        accounts = self.fints_client.get_sepa_accounts()

        self.selected_account = None
        for account in accounts:
            if account.iban == iban:
                self.selected_account = account
                break

        if self.selected_account is None:
            raise AccountNotFoundException(accounts)

    def get_transactions(
        self, start_date: Optional[datetime.datetime] = None,
    ) -> List[Transaction]:
        """
        Get transactions for the selected account.
        """
        return self.fints_client.get_transactions(
            self.selected_account, start_date=start_date
        )
