FROM python:3.7

COPY . /app
WORKDIR /app
RUN pip install .

CMD ["ing-ynab"]
