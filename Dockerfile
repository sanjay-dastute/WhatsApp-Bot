FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install flask

COPY . .

ENV FLASK_APP=app.main
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:${PATH}"

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
