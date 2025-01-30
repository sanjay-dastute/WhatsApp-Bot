FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

ENV FLASK_APP=app.main
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8000"]
