FROM python:3.9.19-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "src/main.py"]
