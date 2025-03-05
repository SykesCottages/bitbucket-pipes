FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN chmod +x main.py

ENTRYPOINT ["python", "/app/main.py"]