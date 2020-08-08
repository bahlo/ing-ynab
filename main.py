from datetime import datetime, date
import json
import os

from dotenv import load_dotenv
import requests

BASE_URL = "https://api.youneedabudget.com/v1"


def import_transactions(transactions):
    headers = {"Authorization": "Bearer " + os.environ["YNAB_ACCESS_TOKEN"]}
    payload = {
        "transactions": transactions,
    }
    path = "/budgets/" + os.environ["YNAB_BUDGET_ID"] + "/transactions"
    r = requests.post(BASE_URL + path, json=payload, headers=headers)
    r.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    import_transactions(
        [
            {
                "account_id": os.environ["YNAB_ACCOUNT_ID"],
                "date": datetime.now().isoformat(),
                "amount": 13370,
                "cleared": "cleared",
                "memo": "hello from python",
            },
        ]
    )
