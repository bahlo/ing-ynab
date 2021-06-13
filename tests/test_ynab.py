import unittest
from datetime import date
from mt940.models import Transaction, Amount

from ing_ynab.ynab import YNABClient


class TestTransformTransactions(unittest.TestCase):
    def test_correct_hash(self):
        account_id = "abcdef"
        flag_color = "orange"
        ynab_client = YNABClient("", account_id, "", flag_color=flag_color)

        transactions = [
            Transaction(
                [],
                data={
                    "date": date.fromisoformat("2020-01-11"),
                    "applicant_name": "foo",
                    "purpose": "bar",
                    "amount": Amount("42.24", "C"),
                },
            ),
            Transaction(
                [],
                data={
                    "date": date.fromisoformat("2020-08-11"),
                    "applicant_name": "bar",
                    "purpose": "baz",
                    "amount": Amount("1337", "D"),
                },
            ),
        ]
        transformed = ynab_client.transform_transactions(transactions)
        self.assertEqual(2, len(transformed))
        self.assertEqual(
            {
                "account_id": account_id,
                "date": "2020-01-11",
                "amount": 42240,
                "payee_name": "foo",
                "cleared": "cleared",
                "memo": "bar",
                "flag_color": flag_color,
                "import_id": "YNAB:42240:2020-01-11:1",
            },
            transformed[0],
        )
        self.assertEqual(
            {
                "account_id": account_id,
                "date": "2020-08-11",
                "amount": -1337000,
                "payee_name": "bar",
                "cleared": "cleared",
                "memo": "baz",
                "flag_color": flag_color,
                "import_id": "YNAB:-1337000:2020-08-11:1",
            },
            transformed[1],
        )

    def test_correct_import_id_occurence(self):
        ynab_client = YNABClient("", "abcdef", "")

        transactions = [
            Transaction(
                [],
                data={
                    "date": date.fromisoformat("2020-06-13"),
                    "applicant_name": "foo",
                    "purpose": "bar",
                    "amount": Amount("42.24", "D"),
                },
            ),
            Transaction(
                [],
                data={
                    "date": date.fromisoformat("2020-06-13"),
                    "applicant_name": "foo",
                    "purpose": "bar",
                    "amount": Amount("42.24", "D"),
                },
            ),
        ]
        transformed = ynab_client.transform_transactions(transactions)

        self.assertEqual(2, len(transformed))
        self.assertEqual(transformed[0]["import_id"], "YNAB:-42240:2020-06-13:1")
        self.assertEqual(transformed[1]["import_id"], "YNAB:-42240:2020-06-13:2")
