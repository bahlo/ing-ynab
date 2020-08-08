from datetime import datetime
import os
from dotenv import load_dotenv
import ynab

if __name__ == "__main__":
    load_dotenv()
    ynab.import_transactions(
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
