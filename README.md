![ing-ynab logo](logo.jpg)

[![ci](https://github.com/bahlo/fints_ynab/workflows/ci/badge.svg)](https://github.com/bahlo/ing-ynab/actions?query=workflow%3Aci)
[![PyPI](https://img.shields.io/pypi/v/ing-ynab)](https://pypi.org/project/ing-ynab)
![PyPI - License](https://img.shields.io/pypi/l/ing-ynab)

Import your ING Germany bank statements via FinTS into YNAB.

## Setup

Before setting this up, you need to
[register your FinTS product](#how-do-i-register-the-fints-product)
– it's free and takes only a few days.

Since this application will need your ING pin and YNAB access token it's
recommended to run this in your local network (could be a Raspberry Pi, it's
pretty light).

To start the application you need Python 3.12 or higher as well as
[pdm](https://pdm-project.org/en/latest/).

```sh
$ pdm install
$ pdm run start
```

Alternatively you can use the Docker image from `ghcr.io/bahlo/ing-ynab:latest`
or `ghcr.io/bahlo/ing-ynab:3.0.1`.

## Configuration

The configuration is done via environment variables:

- `FINTS_PRODUCT_ID`: Your FinTS product ID (defaults to python-fints one).
- `ING_LOGIN`: The login id of your ING account.
- `ING_IBAN`: The IBAN of the account you want to add.
- `ING_PIN`: The pin of your ING account (leave empty to be prompted).
- `YNAB_ACCESS_TOKEN`: Go to your budget settings to create one (leave empty
  to be prompted).
- `YNAB_BUDGET_ID`: On the webpage of your budget the first UUID in the path (`https://app.youneedabudget.com/<BUDGET_UUID>/budget/202109`).
- `YNAB_ACCOUNT_ID`: On the webpage of the bank account the last UUID in the path (`https://app.youneedabudget.com/<BUDGET_UUID>/accounts/<BANK_ACCOUNT_UUID>`).
- `YNAB_FLAG_COLOR`: If set, use that color for the imported transactions.
- `DEBUG`: Set to `1` to enable debug output and print transactions instead of
  importing them.

## Security

You can pass in your bank pin and YNAB access token via environment variables,
if you like. This has the drawback that anyone with system access can read
and potentially use them so it's discouraged (but supported).

The alternative is not specifying `YNAB_ACCESS_TOKEN` and/or `ING_PIN`, which
will cause the application to prompt you on startup. This has the drawback that
you need to input them everytime the application restarts.

For docker you'll need to pass the `-it` flags to be able to input these
variables. For docker-compose, add these fields:

```yml
tty: true
stdin_open: true
```

After starting with `docker-compose up -d`, run `docker attach $container_id`
to attach to the container. Note that the prompt for the pin might be hidden,
so you have to enter the pin directly.

## FAQ

### Why is this ING-only? Isn't FinTS a general protocol?

It is, but the implementations differ a lot. This actually started out as a
general-purpose library but I can only really test ING and I rather have a
specialised library than a multipurpose one where I can't guarantee
functionality.

### Can you support my bank?

The [python-fints](https://github.com/raphaelm/python-fints) library supports
a lot of banks, so probably. But we need to work together as I can't test it.
Feel free to get in touch: <hey@arne.me>

### How do I register the FinTS product?

1. Go to the [FinTS product registration](https://www.hbci-zka.de/register/prod_register.htm)
2. Click `Registrierungsprozess` to get to a PDF form
3. Fill in your data. If you don't know what else to put, here are some suggestions:
   - `Firmenbezeichnung`: Your name
   - `Produktname`: `ing-ynab`
   - `Produktkategorie`: `Web-Server`
4. Send the form to the email adress on the last page

After a week or two you will get your product id via email.
