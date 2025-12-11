FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==3.0.3

COPY deploy ./deploy

WORKDIR /app/deploy

EXPOSE 5000

CMD ["python", "app.py"]
