import unittest
from datetime import datetime
from mt940.models import Transaction, Amount

from ing_ynab.ynab import transform_transactions


class TestTransformTransactions(unittest.TestCase):
    def test_correct_hash(self):
        transactions = [
            Transaction(
                [],
                data={
                    "date": datetime.fromisoformat("2020-01-11T13:20:00"),
                    "applicant_name": "foo",
                    "purpose": "bar",
                    "amount": Amount("42.24", "C"),
                },
            ),
            Transaction(
                [],
                data={
                    "date": datetime.fromisoformat("2020-08-11T13:20:00"),
                    "applicant_name": "bar",
                    "purpose": "baz",
                    "amount": Amount("1337", "D"),
                },
            ),
        ]
        account_id = "abcdef"
        flag_color = "orange"
        transformed = transform_transactions(
            transactions, account_id, flag_color=flag_color
        )
        self.assertEqual(2, len(transformed))
        self.assertEqual(
            {
                "account_id": account_id,
                "date": "2020-01-11T13:20:00",
                "amount": 42240,
                "payee_name": "foo",
                "cleared": "cleared",
                "memo": "bar",
                "flag_color": flag_color,
            },
            transformed[0],
        )
        self.assertEqual(
            {
                "account_id": account_id,
                "date": "2020-08-11T13:20:00",
                "amount": -1337000,
                "payee_name": "bar",
                "cleared": "cleared",
                "memo": "baz",
                "flag_color": flag_color,
            },
            transformed[1],
        )
