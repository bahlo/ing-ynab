import unittest
from decimal import Decimal
from datetime import datetime
from mt940.models import Transaction

from ing_ynab.ing import hash_transaction


class TestHashTransaction(unittest.TestCase):
    def test_correct_hash(self):
        data = {
            "date": datetime.fromisoformat("2020-08-11T13:20:00"),
            "applicant_name": "foo",
            "purpose": "bar",
            "amount": Decimal("42.24"),
        }
        hash = hash_transaction(Transaction([], data=data))
        self.assertEqual(
            hash, "c1b017447122828744a8d7ef21cb981675f3c99235ff31dfb7a3dab494c80934"
        )
