ARG PYTHON_BASE=3.12-slim
FROM python:$PYTHON_BASE AS builder
RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false
COPY pyproject.toml pdm.lock README.md /project/
COPY src/ /project/src
WORKDIR /project
RUN pdm install --check --prod --no-editable

FROM python:$PYTHON_BASE
COPY --from=builder /project/.venv/ /project/.venv
ENV PATH="/project/.venv/bin:$PATH"
COPY src /project/src
WORKDIR /project/src
CMD ["python", "-m", "ing_ynab"]
