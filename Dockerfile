FROM python:3.13-slim

ENV POETRY_VERSION=1.7.1
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /app
COPY . .

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
