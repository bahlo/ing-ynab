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
        ynab_client = YNABClient("", "foo", "")

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

    def test_paypal_extraction(self):
        ynab_client = YNABClient("", "foo", "")

        tests = [
            {
                "name": "no pp",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": ". POSTSHOP, Ihr Einkauf bei POSTSHOP",
                        "amount": Amount("1.55", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL POSTSHOP",
                },
            },
            {
                "name": "pp",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . GITHUB INC, Ihr Einkauf bei GITHUB INC",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL GITHUB INC",
                },
            },
            {
                "name": "linebreak",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . GITHUB INC, Ihr Einkauf be\ni GITHUB INC",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL GITHUB INC",
                },
            },
            {
                "name": "missing space after bei",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . GITHUB INC, Ihr Einkauf beiGITHUB INC",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL GITHUB INC",
                },
            },
            {
                "name": "missing space before bei",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . GITHUB INC, Ihr Einkaufbei GITHUB INC",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL GITHUB INC",
                },
            },
            {
                "name": "lastschrift",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . PAYPAL.ZAHLUNG UBER LASTSCHRIFT an GITHUB INC",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL GITHUB INC",
                },
            },
            {
                "name": "lastschrift",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": "PP.0000.PP . iTunes and App Store,Ihr Einkauf beiiTunes and App Store",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL iTunes and App Store",
                },
            },
            {
                "name": "lastschrift",
                "transaction": Transaction(
                    [],
                    data={
                        "date": date.fromisoformat("2020-08-18"),
                        "applicant_name": "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
                        "purpose": ". PAYPAL.ZAHLUNG UBER LASTSCHRIFT an example.orgABBUCHUNG VOM PAYPAL.KONTO",
                        "amount": Amount("4.99", "D"),
                    },
                ),
                "expected": {
                    "payee_name": "PAYPAL example.org",
                },
            },
        ]

        for test in tests:
            transformed = ynab_client.transform_transactions([test["transaction"]])
            for key in test["expected"]:
                self.assertEqual(
                    test["expected"][key], transformed[0][key], test["name"]
                )

    def test_paypal_applicant_names(self):
        ynab_client = YNABClient("", "foo", "")

        # For some reason, PayPal has a different payee names, test some of them
        tests = [
            "PayPal (Europe) S.a.r.l. et Cie., S.C.A.",
            "PayPal (Europe) S.a.r.l. etCie., S.C.A.",
            "PayPal (Europe) S.a.r.l.et Cie., S.C.A.",
            "PayPal (Europe)S.a.r.l. et Cie., S.C.A.",
            "PayPal(Europe) S.a.r.l. et Cie., S.C.A.",
        ]
        for test in tests:
            transformed = ynab_client.transform_transactions(
                [
                    Transaction(
                        [],
                        data={
                            "date": date.fromisoformat("2020-08-18"),
                            "applicant_name": test,
                            "purpose": "PP.0000.PP . GITHUB INC, Ihr Einkauf bei GITHUB INC",
                            "amount": Amount("1.55", "D"),
                        },
                    )
                ]
            )
            self.assertEqual("PAYPAL GITHUB INC", transformed[0]["payee_name"])
