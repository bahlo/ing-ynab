FROM python:3.8

RUN pip install pipenv

COPY . /app
WORKDIR /app

RUN pipenv install --deploy
CMD ["pipenv", "run", "python", "ing_ynab"]