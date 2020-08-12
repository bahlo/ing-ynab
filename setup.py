from setuptools import find_packages, setup

from ing_ynab import VERSION

setup(
    name="ing_ynab",
    version=VERSION,
    description="Import your ING Germany bank statements via FinTS into YNAB",
    url="https://github.com/bahlo/ing_ynab",
    author="Arne Bahlo",
    author_email="hallo@arne.me",
    license="MIT",
    keywords="ing ynab fints",
    packages=find_packages(include=["ing_ynab"]),
)
