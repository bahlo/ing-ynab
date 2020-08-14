from setuptools import setup, find_packages

from ing_ynab import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ing_ynab",
    version=VERSION,
    description="Import your ING Germany bank statements via FinTS into YNAB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bahlo/ing_ynab",
    author="Arne Bahlo",
    author_email="hallo@arne.me",
    license="MIT",
    keywords="ing ynab fints",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "bleach==3.1.5; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "certifi==2020.6.20",
        "chardet==3.0.4",
        "elementpath==1.4.6",
        "fints==3.0.0",
        "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "mt-940==4.23.0",
        "packaging==20.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pyparsing==2.4.7; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dotenv==0.14.0",
        "requests==2.24.0",
        "sepaxml==2.3.0",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "text-unidecode==1.3",
        "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
        "webencodings==0.5.1",
        "xmlschema==1.2.2",
    ],
    dependency_links=[],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["ing-ynab=ing_ynab.cli:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
    ],
)
