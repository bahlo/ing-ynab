"""
Provides methods to work with the YNAB API.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from mt940.models import Transaction as FinTSTransaction
import requests

YNAB_BASE_URL = "https://api.youneedabudget.com/v1"


class YNABError(Exception):
    """
    YNABError is raised when YNAB returns an error.
    """


class YNABClient:
    """
    YNABClient provides methods to transform and import transactions into YNAB.
    """

    access_token: str
    account_id: str
    budget_id: str
    flag_color: Optional[str]

    def __init__(
        self,
        access_token: str,
        account_id: str,
        budget_id: str,
        flag_color: Optional[str] = None,
    ):
        self.access_token = access_token
        self.account_id = account_id
        self.budget_id = budget_id
        self.flag_color = flag_color

    def import_transactions(self, transactions: List[Dict[str, str]]) -> List[int]:
        """
        Import the transaction into YNAB, returns an array with transaction ids.
        """
        headers = {"Authorization": "Bearer " + self.access_token}
        payload = {
            "transactions": transactions,
        }
        path = "/budgets/" + self.budget_id + "/transactions"
        response = requests.post(YNAB_BASE_URL + path, json=payload, headers=headers)
        body = response.json()
        if response.status_code >= 400:
            raise YNABError(body["error"]["detail"])
        return body["data"]["transaction_ids"]

    def transform_transactions(
        self, transactions: List[FinTSTransaction],
    ) -> List[Dict[str, str]]:
        """
        Transform the FinTS transactions into something the YNAB API understands.
        """
        transformed = []
        for transaction in transactions:
            data = transaction.data

            # ING sometimes adds transactions that are dated to the future.
            # YNAB doesn't support this, so since the transaction already
            # happened anyway, we're overriding the date.
            date = data["date"]
            if date > datetime.now():
                date = datetime.now()

            transformed.append(
                {
                    "account_id": self.account_id,
                    "date": date.isoformat(),
                    "amount": int(data["amount"].amount * Decimal("1000.0")),
                    "payee_name": data["applicant_name"],
                    "cleared": "cleared",
                    "memo": data["purpose"],
                    "flag_color": self.flag_color,
                }
            )
        return transformed
