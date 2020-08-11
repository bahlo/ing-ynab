"""
Provides methods to work with the YNAB API.
"""
from decimal import Decimal
from typing import List, Optional, Dict
from mt940.models import Transaction as FinTSTransaction
import requests

# https://github.com/PyCQA/pylint/issues/647
# pylint: disable=C0330

YNAB_BASE_URL = "https://api.youneedabudget.com/v1"


def import_transactions(
    ynab_transactions: List[Dict[str, str]],
    ynab_access_token: str,
    ynab_budget_id: str,
) -> List[int]:
    """
    Import the transaction into YNAB, returns an array with transaction ids.
    """
    headers = {"Authorization": "Bearer " + ynab_access_token}
    payload = {
        "transactions": ynab_transactions,
    }
    path = "/budgets/" + ynab_budget_id + "/transactions"
    response = requests.post(YNAB_BASE_URL + path, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["transaction_ids"]


def transform_transactions(
    transactions: List[FinTSTransaction],
    account_id: str,
    flag_color: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Transform the FinTS transactions into something the YNAB API understands.
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
