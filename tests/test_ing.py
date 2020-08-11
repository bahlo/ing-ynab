import unittest
from decimal import Decimal
from datetime import datetime
from mt940.models import Transaction

from ing_ynab import ing


class TestHashTransaction(unittest.TestCase):
    def test_correct_hash(self):
        data = {
            "date": datetime.fromisoformat("2020-08-11T13:20:00"),
            "applicant_name": "foo",
            "purpose": "bar",
            "amount": Decimal("42.24"),
        }
        hash = ing.hash_transaction(Transaction([], data=data))
        self.assertEqual(
            hash, "7b13f79818b44944607b49b0a700e8b820c8389df8ef90a65e7657df5d3ded9a"
        )
