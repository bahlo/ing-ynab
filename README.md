# ing-ynab ![build](https://github.com/bahlo/fints_ynab/workflows/build/badge.svg)

Import your ING (de) bank statements via FinTS into YNAB.

## Development setup

1. Clone this repository
2. Install [pipenv](https://pipenv.pypa.io/en/latest/)
3. Run `pipenv shell`

## Configuration

The configuration is done via environment variables:

* `START_DATE`: The date to start getting transactions.

### YNAB

* `YNAB_ACCESS_TOKEN`: Go to your budget settings to create one.
* `YNAB_BUDGET_ID`: On the webpage of your budget the last number in the path.
* `YNAB_ACCOUNT_ID`: On the webpage of the account the last uuid in the path.

### FinTS

* `FINTS_LOGIN`: The login id of your ING account (the last ten digits of your IBAN).
* `FINTS_IBAN`: The IBAN of the account you want to add.
* `FINTS_PIN`: The ping (password) of your ING account (leave empty to be prompted).
* `FINTS_PRODUCT_ID`: Your FinTS product ID (leave empty to use the python-fints one, though that's discouraged).
